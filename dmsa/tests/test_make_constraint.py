from __future__ import unicode_literals

from sqlalchemy.schema import (PrimaryKeyConstraint, ForeignKeyConstraint,
                               UniqueConstraint)
from dmsa.makers import make_constraint
from nose.tools import eq_, ok_

CONSTRAINT_MAP = {
    'primary_keys': PrimaryKeyConstraint,
    'foreign_keys': ForeignKeyConstraint,
    'uniques': UniqueConstraint
}


def test_name():

    for con_type, con_class in list(CONSTRAINT_MAP.items()):

        if con_type == 'foreign_keys':
            con_json = {'name': 'test_con', 'source_field': 'id',
                        'target_table': 'foo', 'target_field': 'bar'}
        else:
            con_json = {'name': 'test_con', 'fields': ['id']}

        constraint = make_constraint(con_type, con_json)
        yield check_name, constraint, 'test_con'


def check_name(constraint, name):
    eq_(constraint.name, name)


def test_types():

    for con_type, con_class in list(CONSTRAINT_MAP.items()):

        if con_type == 'foreign_keys':
            con_json = {'name': 'test_con', 'source_field': 'id',
                        'target_table': 'foo', 'target_field': 'bar'}
        else:
            con_json = {'name': 'test_con', 'fields': ['id']}

        constraint = make_constraint(con_type, con_json)
        assert isinstance(constraint, con_class)


def test_fields():

    for con_type, con_class in list(CONSTRAINT_MAP.items()):

        if con_type == 'foreign_keys':
            con_json = {'name': 'test_con', 'source_field': 'id',
                        'target_table': 'foo', 'target_field': 'bar'}
        else:
            con_json = {'name': 'test_con', 'fields': ['id']}

        constraint = make_constraint(con_type, con_json)

        if con_type == 'foreign_keys':
            eq_(constraint.column_keys, ['id'])
            eq_(constraint.elements[0].target_fullname, 'foo.bar')
        else:
            eq_(constraint._pending_colargs, ['id'])


def test_foreign_key_use_alter():

    con_type = 'foreign_keys'
    con_json = {'name': 'test_con', 'source_field': 'id',
                'target_table': 'foo', 'target_field': 'bar'}

    constraint = make_constraint(con_type, con_json)
    ok_(constraint.use_alter)
