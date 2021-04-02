from __future__ import unicode_literals


def get_datatype_map():
    from sqlalchemy import (Integer, Numeric, Float, String, Date,
                            DateTime, Time, Text, Boolean, LargeBinary,BigInteger)

    return {
        'integer': Integer,
        'number': Numeric,
        'decimal': Numeric,
        'float': Float,
        'string': String,
        'date': Date,
        'datetime': DateTime,
        'timestamp': DateTime,
        'time': Time,
        'text': Text,
        'clob': Text,
        'boolean': Boolean,
        'blob': LargeBinary,
        'biginteger': BigInteger
    }


def make_index(index_json):
    """Returns a dynamically constructed SQLAlchemy model Index class.

    `index_json` is a declarative style dictionary index object, as defined by
    the chop-dbhi/data-models package.
    """

    from sqlalchemy.schema import Index

    # Transform empty string to None in order to trigger auto-generation.

    idx_name = index_json.get('name')

    return Index(idx_name, *index_json['fields'])


def make_constraint(constraint_type, constraint_json):
    """Returns a dynamically constructed SQLAlchemy model Constraint class.

    `constraint_type` is a string that maps to the type of constraint to be
    constructed.

    `constraint_json` is a declarative style dictionary constraint object, as
    defined by the chop-dbhi/data-models package.
    """

    from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint,
                                   UniqueConstraint)

    # Transform empty string to None in order to trigger auto-generation.

    constraint_name = constraint_json.get('name')

    # Create the appropriate constraint class.

    if constraint_type == 'primary_keys':

        return PrimaryKeyConstraint(*constraint_json['fields'],
                                    name=constraint_name)

    elif constraint_type == 'foreign_keys':

        source_column_list = [constraint_json['source_field']]
        target_column_list = ['.'.join([constraint_json['target_table'],
                                        constraint_json['target_field']])]

        return ForeignKeyConstraint(source_column_list, target_column_list,
                                    constraint_name, use_alter=True)

    elif constraint_type == 'uniques':

        return UniqueConstraint(*constraint_json['fields'],
                                name=constraint_name)


def make_column(field, not_null_flag=False):
    """Returns a dynamically constructed SQLAlchemy model Column class.

    `field` is a declarative style dictionary field object retrieved from the
    chop-dbhi/data-models service or at least matching the format specified
    there.

    `not_null_flag` signifies that a not null constraint should be included.
    """

    from sqlalchemy import (Column, String, Numeric)

    column_kwargs = {}
    column_kwargs['name'] = field['name']

    type_string = field['type']
    DATATYPE_MAP = get_datatype_map()
    type_class = DATATYPE_MAP[type_string]
    type_kwargs = {}

    if field.get('description'):
        # This only exists in the ORM, will not generate a DB "comment".
        column_kwargs['doc'] = field['description']

    if field.get('default'):
        # The first is for the ORM, the second for the DB.
        column_kwargs['default'] = field['default']
        column_kwargs['server_default'] = field['default']

    if not_null_flag:
        column_kwargs['nullable'] = False

    if type_class == String:
        type_kwargs['length'] = field.get('length') or 256

    if type_class == Numeric:
        type_kwargs['precision'] = field.get('precision') or 20
        type_kwargs['scale'] = field.get('scale') or 5

    column_kwargs['type_'] = type_class(**type_kwargs)
    return Column(**column_kwargs)


def make_table(table_json, metadata, not_nulls):
    """Makes and attaches a SQLAlchemy Table class to the metadata object.

    `table_json` is a declarative style nested table object retrieved from the
    chop-dbhi/data-models service or at least matching the format specified
    there.

    `metadata` is the metadata instance the produced model should attach to.
    This could simply be sqlalchemy.MetaData().

    `not_nulls` is a list of table-relevant not null constraints matching the
    chop-dbhi/data-models specified format.
    """

    from sqlalchemy import Table

    table = Table(table_json['name'], metadata)

    fields = table_json.get('fields', []) or []

    for field in fields:

        not_null_flag = False

        for not_null in not_nulls:
            if not_null['field'] == field['name']:
                not_null_flag = True
                break

        table.append_column(make_column(field, not_null_flag))

    return table


def make_model(data_model, metadata):
    """Makes and attaches a collection of SQLAlchemy classes that describe a
    data model to the metadata object.

    `data_model` is a declarative style nested data model object retrieved from
    the chop-dbhi/data-models service or at least matching the format specified
    there.

    `metadata` is the metadata instance the produced models should attach to.
    This could simply be sqlalchemy.MetaData().
    """

    for table_json in data_model['tables']:

        # Construct table-relevant not-null constraint list.

        table_not_nulls = []

        for not_null in data_model['schema']['constraints']['not_null'] or []:

            if not_null['table'] == table_json['name']:

                table_not_nulls.append(not_null)

        # Construct and attach table to metadata.

        make_table(table_json, metadata, table_not_nulls)

    # Construct and add constraints to the relevant tables.

    for con_type, con_list in \
            data_model['schema']['constraints'].iteritems():

        if con_type != 'not_null':

            for con in con_list or []:

                table_name = con.get('table') or con.get('source_table')
                metadata.tables[table_name].\
                    append_constraint(make_constraint(con_type, con))

    # Construct and add indexes to the relevant tables.

    for index in data_model['schema']['indexes']:

        table_name = index['table']
        metadata.tables[table_name].append_constraint(make_index(index))

    return metadata


def make_model_from_service(model, model_version, service, metadata):
    from dmsa.utility import get_model_json
    return make_model(get_model_json(model, model_version, service), metadata)
