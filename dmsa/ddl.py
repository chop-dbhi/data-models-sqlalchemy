from sqlalchemy import (create_engine, MetaData, Table, Column,
                        Integer, Numeric, String, DateTime, text)
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import (CreateTable, AddConstraint, CreateIndex,
                               DropTable, DropConstraint, DropIndex,
                               ForeignKeyConstraint, CheckConstraint,
                               UniqueConstraint, PrimaryKeyConstraint)
from dmsa import __version__
from dmsa.utility import get_model_json, get_service_version
from dmsa.makers import make_model


# Coerce Numeric type to produce NUMBER on Oracle backend.
@compiles(Numeric, 'oracle')
def _compile_numeric_oracle(type_, compiler, **kw):
    return 'NUMBER'


# and Integer type to produce NUMBER(10) on Oracle backend.
@compiles(Integer, 'oracle')
def _compile_integer_oracle(type_, compiler, **kw):
    return 'NUMBER(10)'


# Coerce String type without length to produce VARCHAR2(255) on Oracle.
@compiles(String, 'oracle')
def _compile_string_oracle(type_, compiler, **kw):

    if not type_.length:
        type_.length = 255
    visit_attr = 'visit_{0}'.format(type_.__visit_name__)
    return getattr(compiler, visit_attr)(type_, **kw)


# Coerce String type without length to produce VARCHAR(255) on MySQL.
@compiles(String, 'mysql')
def _compile_string_mysql(type_, compiler, **kw):

    if not type_.length:
        type_.length = 255
    visit_attr = 'visit_{0}'.format(type_.__visit_name__)
    return getattr(compiler, visit_attr)(type_, **kw)


# Add DEFERRABLE INITIALLY DEFERRED to Oracle constraints.
@compiles(ForeignKeyConstraint, 'oracle')
@compiles(UniqueConstraint, 'oracle')
@compiles(CheckConstraint, 'oracle')
def _compile_constraint_oracle(constraint, compiler, **kw):

    constraint.deferrable = True
    constraint.initially = 'DEFERRED'
    visit_attr = 'visit_{0}'.format(constraint.__visit_name__)
    return getattr(compiler, visit_attr)(constraint, **kw)


# Add DEFERRABLE INITIALLY DEFERRED to PostgreSQL constraints.
@compiles(ForeignKeyConstraint, 'postgresql')
@compiles(UniqueConstraint, 'postgresql')
@compiles(CheckConstraint, 'postgresql')
def _compile_constraint_postgresql(constraint, compiler, **kw):

    constraint.deferrable = True
    constraint.initially = 'DEFERRED'
    visit_attr = 'visit_{0}'.format(constraint.__visit_name__)
    return getattr(compiler, visit_attr)(constraint, **kw)


def generate(model, model_version, dialect, tables=True, constraints=True,
             indexes=True, drop=False, delete_data=False, nologging=False,
             logging=False,
             service='https://data-models-service.research.chop.edu/'):
    """Generate data definition language for the data model specified in the
    given DBMS dialect.

    Arguments:
      model          Model to generate DDL for.
      model_version  Model version to generate DDL for.
      dialect        DBMS dialect to generate DDL in.
      tables         Include tables when generating DDL.
      constraints    Include constraints when generating DDL.
      indexes        Include indexes when generating DDL.
      drop           Generate DDL to drop, instead of create, objects.
      delete_data    Generate DML to delete data from the model.
      nologging      Generate Oracle DDL to make objects "nologging".
      logging        Generate Oracle DDL to make objects "logging".
      service        Base URL of the data models service to use.
    """  # noqa

    metadata = MetaData()
    model_json = get_model_json(model, model_version, service)
    make_model(model_json, metadata)

    service_version = get_service_version(service)

    engine = create_engine(dialect + '://')

    output = []

    INSERT = ("INSERT INTO version_history (operation, model, model_version, "
              "dms_version, dmsa_version) VALUES ('{operation}', '" +
              model + "', '" + model_version + "', '" +
              service_version + "', '" + __version__ + "');\n\n")

    if dialect.startswith('oracle'):
        INSERT = INSERT + "COMMIT;\n\n"

    version_history = Table(
        'version_history', MetaData(),
        Column('datetime', DateTime(), primary_key=True,
               server_default=text('CURRENT_TIMESTAMP')),
        Column('operation', String(100)),
        Column('model', String(16)),
        Column('model_version', String(50)),
        Column('dms_version', String(50)),
        Column('dmsa_version', String(50))
    )

    version_tbl_ddl = str(CreateTable(version_history).
                          compile(dialect=engine.dialect)).strip()

    if dialect.startswith('mssql'):
        version_tbl_ddl = ("IF OBJECT_ID ('version_history', 'U') IS NULL " +
                           version_tbl_ddl + ";")
    elif dialect.startswith('oracle'):
        version_tbl_ddl = ("BEGIN\n" +
                           "EXECUTE IMMEDIATE '" + version_tbl_ddl + "';\n" +
                           "EXCEPTION\n" +
                           "WHEN OTHERS THEN\n" +
                           "IF SQLCODE = -955 THEN NULL;\n" +
                           "ELSE RAISE;\n" +
                           "END IF;\nEND;\n/")
    else:
        version_tbl_ddl = version_tbl_ddl.replace('CREATE TABLE',
                                                  'CREATE TABLE IF NOT EXISTS')
        version_tbl_ddl = version_tbl_ddl + ";"

    if delete_data:

        output.append(INSERT.format(operation='delete data'))

        tables = reversed(metadata.sorted_tables)
        output.extend(delete_ddl(tables, engine))

        output.insert(0, version_tbl_ddl + '\n\n')

        output = ''.join(output)

        return output

    LOGGING = 'ALTER {type} {name} LOGGING;\n'
    NOLOGGING = 'ALTER {type} {name} NOLOGGING;\n'

    if tables:

        if drop:

            tables = reversed(metadata.sorted_tables)
            output.extend(table_ddl(tables, engine, True))
            output.insert(0, INSERT.format(operation='drop tables'))

        elif logging and dialect.startswith('oracle'):

            output.append(INSERT.format(operation='table logging'))
            for table in metadata.sorted_tables:
                output.append(LOGGING.format(type='TABLE', name=table.name))
            output.append('\n')

        elif nologging and dialect.startswith('oracle'):

            output.append(INSERT.format(operation='table nologging'))
            for table in metadata.sorted_tables:
                output.append(NOLOGGING.format(type='TABLE', name=table.name))
            output.append('\n')

        else:

            output.append(INSERT.format(operation='create tables'))
            tables = metadata.sorted_tables
            output.extend(table_ddl(tables, engine, False))

    if constraints:

        if drop and not dialect.startswith('sqlite'):

            tables = reversed(metadata.sorted_tables)
            output.insert(0, '\n')
            output[0:0] = constraint_ddl(tables, engine, True)
            output.insert(0, INSERT.format(operation='drop constraints'))

        elif logging:
            pass
        elif nologging:
            pass

        elif not dialect.startswith('sqlite'):

            output.append('\n')
            output.append(INSERT.format(operation='create constraints'))
            tables = metadata.sorted_tables
            output.extend(constraint_ddl(tables, engine, False))

    if indexes:

        if drop:

            tables = reversed(metadata.sorted_tables)
            output.insert(0, '\n')
            output[0:0] = index_ddl(tables, engine, True)
            output.insert(0, INSERT.format(operation='drop indexes'))

        elif logging and dialect.startswith('oracle'):

            output.append(INSERT.format(operation='index logging'))
            for table in metadata.sorted_tables:
                output.append(LOGGING.format(type='INDEX', name=table.name))
            output.append('\n')

        elif nologging and dialect.startswith('oracle'):

            output.append(INSERT.format(operation='index nologging'))
            for table in metadata.sorted_tables:
                output.append(NOLOGGING.format(type='INDEX', name=table.name))
            output.append('\n')

        else:

            output.append('\n')
            output.append(INSERT.format(operation='create indexes'))
            tables = metadata.sorted_tables
            output.extend(index_ddl(tables, engine, False))

    output.insert(0, version_tbl_ddl + '\n\n')

    output = ''.join(output)

    return output


def delete_ddl(tables, engine):

    output = []

    for table in tables:
        output.append(str(table.delete().compile(dialect=engine.dialect)).
                      strip())
        output.append(';\n\n')

    return output


def table_ddl(tables, engine, drop=False):

    output = []

    for table in tables:

        if not drop:
            ddl = CreateTable(table)
        else:
            ddl = DropTable(table)

        output.append(str(ddl.compile(dialect=engine.dialect)).strip())
        output.append(';\n\n')

    return output


def constraint_ddl(tables, engine, drop=False):

    output = []

    for table in tables:
        constraints = sorted(list(table.constraints), key=lambda k: k.name,
                             reverse=drop)
        for constraint in constraints:

            # Avoid duplicating primary key constraint definitions (they are
            # included in CREATE TABLE statements).
            if not isinstance(constraint, PrimaryKeyConstraint):

                if not drop:
                    ddl = AddConstraint(constraint)
                else:
                    ddl = DropConstraint(constraint)

                output.append(str(ddl.compile(dialect=engine.dialect)).strip())
                output.append(';\n\n')

    return output


def index_ddl(tables, engine, drop=False):

    output = []

    for table in tables:
        indexes = sorted(list(table.indexes), key=lambda k: k.name,
                         reverse=drop)
        for index in indexes:

            if not drop:
                ddl = CreateIndex(index)
            else:
                ddl = DropIndex(index)

            output.append(str(ddl.compile(dialect=engine.dialect)).strip())
            output.append(';\n\n')

    return output
