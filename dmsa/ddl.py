#! /usr/bin/env python

import sys
import urllib
import json
from sqlalchemy import create_engine, MetaData
from sqlalchemy import Integer, Numeric
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import CreateTable, AddConstraint, CreateIndex
from sqlalchemy.schema import (ForeignKeyConstraint, CheckConstraint,
                               UniqueConstraint)
from dmsa.settings import get_url
from dmsa.makers import make_model


# Coerce Numeric type to produce NUMBER on Oracle backend.
@compiles(Numeric, 'oracle')
def _compile_numeric_oracle(type_, compiler, **kw):
    return 'NUMBER'


# and Integer type to produce NUMBER(10) on Oracle backend.
@compiles(Integer, 'oracle')
def _compile_integer_oracle(type_, compiler, **kw):
    return 'NUMBER(10)'


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


def main(argv=None):
    usage = """Data Model DDL Generator

    Generates data definition language for the data model specified in the
    given DBMS dialect. If passing a custom URL, the data model returned must
    be in the JSON format defined by the chop-dbhi/data-models package. See
    http://docs.sqlalchemy.org/en/rel_1_0/dialects/index.html for available
    dialects. The generated DDL is written to stdout.

    Usage: ddl.py [options] <model> <version> <dialect>

    Options:
        -h --help            Show this screen.
        -t --xtables         Exclude tables from the generated DDL.
        -c --xconstraints    Exclude constraints from the generated DDL.
        -i --xindexes        Exclude indexes from the generated DDL.
        -u URL --url=URL     Retrieve model JSON from this URL instead of the
                             default or environment-variable-passed URL.
        -r --return          Return DDL as python string object instead of
                             printing it to stdout.

    """  # noqa

    from docopt import docopt

    # Ignore command name if called from command line.
    argv = argv or sys.argv[1:]

    args = docopt(usage, argv=argv, version='0.3')

    url = args['--url'] or get_url(args['<model>'], args['<version>'])
    model_json = json.loads(urllib.urlopen(url).read())

    metadata = MetaData()
    make_model(model_json, metadata)

    engine = create_engine(args['<dialect>'] + '://')

    output = ''

    if not args['--xtables']:

        for table in metadata.sorted_tables:

            output += str(CreateTable(table).
                          compile(dialect=engine.dialect)).strip()

            # The compile function does not output a statement terminator.
            output += ';\n\n'

    if not args['--xconstraints']:

        output += '\n'

        for table in metadata.sorted_tables:

            for constraint in table.constraints:

                # Avoid auto-generated empty primary key constraints.
                if list(constraint.columns):

                    output += str(AddConstraint(constraint).
                                  compile(dialect=engine.dialect)).strip()

                    # The compile function does not output a terminator.
                    output += ';\n\n'

    if not args['--xindexes']:

        output += '\n'

        for table in metadata.sorted_tables:

            for index in table.indexes:

                output += str(CreateIndex(index).
                              compile(dialect=engine.dialect)).strip()

                # The compile function does not output a statement terminator.
                output += ';\n\n'

    if args['--return']:
        return output
    else:
        sys.stdout.write(output)


if __name__ == '__main__':
    main()
