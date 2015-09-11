from __future__ import unicode_literals

from sqlalchemy import MetaData
from sqlalchemy.schema import ForeignKeyConstraint, UniqueConstraint
from nose.tools import eq_, ok_
from dmsa.makers import make_model

model_json = {
    'schema': {
        'constraints': {
            'foreign_keys': [{'source_table': 'test_table_1',
                              'source_field': 'integer',
                              'target_table': 'test_table_2',
                              'target_field': 'integer'}],
            'not_null': [{'table': 'test_table_1', 'field': 'string'}],
            'uniques': [{'table': 'test_table_2', 'fields': ['integer']}],
            'primary_keys': [{'table': 'test_table_1', 'fields': ['pk']}]
        },
        'indexes': [{'table': 'test_table_2', 'fields': ['string']}]
    },
    'tables': [{'name': 'test_table_1', 'fields': [{'type': 'integer',
                                                    'name': 'pk'},
                                                   {'type': 'integer',
                                                    'name': 'integer'},
                                                   {'type': 'string',
                                                    'name': 'string',
                                                    'length': 0}]},
               {'name': 'test_table_2', 'fields': [{'type': 'integer',
                                                    'name': 'integer'},
                                                   {'type': 'string',
                                                    'name': 'string',
                                                    'length': 0}]}]
}


def test_pk():

    metadata = MetaData()
    metadata = make_model(model_json, metadata)

    tbl1 = metadata.tables['test_table_1']
    ok_('pk' in tbl1.primary_key.columns)


def test_unique():

    metadata = MetaData()
    metadata = make_model(model_json, metadata)

    tbl2 = metadata.tables['test_table_2']
    for con in tbl2.constraints:
        if isinstance(con, UniqueConstraint):
            ok_('integer' in con.columns)
            break
    else:
        raise AssertionError('UniqueConstraint not found.')


def test_not_null():

    metadata = MetaData()
    metadata = make_model(model_json, metadata)

    tbl1 = metadata.tables['test_table_1']
    col = tbl1.columns['string']
    ok_(not col.nullable)


def test_index():

    metadata = MetaData()
    metadata = make_model(model_json, metadata)

    tbl2 = metadata.tables['test_table_2']
    for idx in tbl2.indexes:
        ok_('string' in idx.columns)
        break
    else:
        raise AssertionError('Index not found.')


def test_foreign_key():

    metadata = MetaData()
    metadata = make_model(model_json, metadata)

    tbl1 = metadata.tables['test_table_1']
    for con in tbl1.constraints:
        if isinstance(con, ForeignKeyConstraint):
            ok_('integer' in con.columns)
            eq_(list(con.columns['integer'].foreign_keys)[0].target_fullname,
                'test_table_2.integer')
            break
    else:
        raise AssertionError('ForeignKeyConstraint not found.')
