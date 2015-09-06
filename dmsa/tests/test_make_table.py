from __future__ import unicode_literals

from nose.tools import eq_, ok_
from sqlalchemy import MetaData
from dmsa.makers import make_table


def test_name():

    table_json = {'name': 'test_table'}
    metadata = MetaData()
    table = make_table(table_json, metadata, [])
    eq_(table.name, 'test_table')


def test_metadata():

    table_json = {'name': 'test_table'}
    metadata = MetaData()
    table = make_table(table_json, metadata, [])
    eq_(metadata.tables[table.name], table)


def test_fields():

    table_json = {'name': 'test_table', 'fields': [{'type': 'integer',
                                                    'name': 'integer'}]}
    metadata = MetaData()
    table = make_table(table_json, metadata, [])
    ok_('integer' in table.columns)


def test_not_null():

    table_json = {'name': 'test_table', 'fields': [{'type': 'integer',
                                                    'name': 'integer'}]}
    not_nulls = [{'table': 'test_table', 'field': 'integer'}]
    metadata = MetaData()
    table = make_table(table_json, metadata, not_nulls)
    ok_(not table.columns['integer'].nullable)
