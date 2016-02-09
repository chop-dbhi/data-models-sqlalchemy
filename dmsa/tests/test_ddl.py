import os
from nose.tools import ok_
from dmsa import ddl

# These testing functions are definitely non-exhaustive. They all operate on
# the OMOP v5.0.0 data model, retrieved from the default data-models-service
# URL (see dmsa.settings; in CircleCI, this is set to localhost and a dms
# is started locally). Additionally, the tests do not check anything about the
# output DDL, merely that the functions run without error and produce non-null
# output strings.

SERVICE = os.environ.get('DMSA_TEST_SERVICE',
                         'http://data-models.origins.link/')

def test_all():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', service=SERVICE)
    ok_(ddl_output)


def test_drop_all():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', drop=True,
                              service=SERVICE)
    ok_(ddl_output)


def test_notables():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', tables=False,
                              service=SERVICE)
    ok_(ddl_output)


def test_drop_notables():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', tables=False,
                              drop=True, service=SERVICE)
    ok_(ddl_output)


def test_noconstraints():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', constraints=False,
                              service=SERVICE)
    ok_(ddl_output)


def test_drop_noconstraints():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', constraints=False,
                              drop=True, service=SERVICE)
    ok_(ddl_output)


def test_noindexes():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', indexes=False,
                              service=SERVICE)
    ok_(ddl_output)


def test_drop_noindexes():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', indexes=False,
                              drop=True, service=SERVICE)
    ok_(ddl_output)


def test_delete():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', delete_data=True)
    ok_(ddl_output)

def test_logging_all():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', logging=True)
    ok_(ddl_output)

def test_nologging_all():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', nologging=True)
    ok_(ddl_output)

def test_logging_notables():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', logging=True,
                              tables=False)
    ok_(ddl_output)

def test_nologging_notables():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', nologging=True,
                              tables=False)
    ok_(ddl_output)

def test_logging_noindexes():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', logging=True,
                              indexes=False)
    ok_(ddl_output)

def test_nologging_noindexes():
    ddl_output = ddl.generate('omop', '5.0.0', 'sqlite', nologging=True,
                              indexes=False)
    ok_(ddl_output)
