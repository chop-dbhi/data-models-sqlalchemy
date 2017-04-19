from __future__ import unicode_literals

from dmsa.makers import make_index
from nose.tools import eq_


def test_name():
    index_json = {'name': 'test_index', 'fields': ['id']}
    index = make_index(index_json)
    eq_(index.name, 'test_index')


def test_fields():
    index_json = {'name': 'test_index', 'fields': ['id']}
    index = make_index(index_json)
    eq_(index.expressions[0], 'id')
