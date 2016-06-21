from __future__ import unicode_literals
from builtins import range

from nose.tools import ok_, eq_
from sqlalchemy import (Integer, Numeric, String, Date, DateTime, Time,
                        Text, Float, Boolean, LargeBinary)
from dmsa.makers import make_column


def test_types():

    fields_json = [
        {'type': 'integer', 'name': 'integer'},
        {'type': 'number', 'name': 'number', 'precision': 10, 'scale': 5},
        {'type': 'decimal', 'name': 'decimal', 'precision': 10, 'scale': 5},
        {'type': 'float', 'name': 'float'},
        {'type': 'string', 'name': 'string', 'length': 128},
        {'type': 'date', 'name': 'date'},
        {'type': 'datetime', 'name': 'datetime'},
        {'type': 'timestamp', 'name': 'timestamp'},
        {'type': 'time', 'name': 'time'},
        {'type': 'text', 'name': 'text'},
        {'type': 'clob', 'name': 'clob'},
        {'type': 'boolean', 'name': 'boolean'},
        {'type': 'blob', 'name': 'blob'}
    ]

    field_types = [
        Integer,
        Numeric,
        Numeric,
        Float,
        String,
        Date,
        DateTime,
        DateTime,
        Time,
        Text,
        Text,
        Boolean,
        LargeBinary
    ]

    for i in range(len(fields_json)):
        field = make_column(fields_json[i])
        yield check_field_type, field, field_types[i]


def check_field_type(field, field_type):
    assert isinstance(field.type, field_type)


def test_doc():

    field_json = {'type': 'string', 'name': 'string',
                  'description': 'test string field'}
    field = make_column(field_json)
    eq_(field.doc, 'test string field')


def test_default():

    field_json = {'type': 'string', 'name': 'string', 'default': 'testing'}
    field = make_column(field_json)
    eq_(field.default.arg, 'testing')
    eq_(field.server_default.arg, 'testing')


def test_nullable():

    field_json = {'type': 'string', 'name': 'string'}
    field = make_column(field_json, True)
    ok_(not field.nullable)


def test_length():

    field_json = {'type': 'string', 'name': 'string', 'length': 128}
    field = make_column(field_json)
    eq_(field.type.length, 128)


def test_length_default():

    field_json = {'type': 'string', 'name': 'string'}
    field = make_column(field_json)
    eq_(field.type.length, 256)


def test_numeric_precision_scale():

    field_json = {'type': 'decimal', 'name': 'decimal', 'precision': 50,
                  'scale': 15}
    field = make_column(field_json)
    eq_(field.type.precision, 50)
    eq_(field.type.scale, 15)


def test_numeric_precision_scale_defaults():

    field_json = {'type': 'decimal', 'name': 'decimal'}
    field = make_column(field_json)
    eq_(field.type.precision, 20)
    eq_(field.type.scale, 5)
