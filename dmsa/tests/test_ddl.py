from nose.tools import ok_
from dmsa import ddl

# These testing functions are definitely non-exhaustive. They all operate on
# the OMOP v5.0.0 data model, retrieved from the default data-models-service
# URL (see dmsa.settings; in CircleCI, this is set to localhost and a dms
# is started locally). Additionally, the tests do not check anything about the
# output DDL, merely that the functions run without error and produce non-null
# output strings.


def test_all():
    ddl_output = ddl.main(['--return', 'omop', '5.0.0', 'sqlite'])
    ok_(ddl_output)


def test_drop_all():
    ddl_output = ddl.main(['--return', '--drop', 'omop', '5.0.0', 'sqlite'])
    ok_(ddl_output)


def test_notables():
    ddl_output = ddl.main(['--return', '--xtables', 'omop', '5.0.0', 'sqlite'])
    ok_(ddl_output)


def test_drop_notables():
    ddl_output = ddl.main(['--return', '--xtables', '--drop', 'omop', '5.0.0',
                           'sqlite'])
    ok_(ddl_output)


def test_noconstraints():
    ddl_output = ddl.main(['--return', '--xconstraints', 'omop', '5.0.0',
                           'sqlite'])
    ok_(ddl_output)


def test_drop_noconstraints():
    ddl_output = ddl.main(['--return', '--xconstraints', '--drop', 'omop',
                           '5.0.0', 'sqlite'])
    ok_(ddl_output)


def test_noindexes():
    ddl_output = ddl.main(['--return', '--xindexes', 'omop', '5.0.0',
                           'sqlite'])
    ok_(ddl_output)


def test_drop_noindexes():
    ddl_output = ddl.main(['--return', '--xindexes', '--drop', 'omop', '5.0.0',
                           'sqlite'])
    ok_(ddl_output)


def test_delete():
    ddl_output = ddl.main(['--return', '--delete-data', 'omop', '5.0.0',
                           'sqlite'])
    ok_(ddl_output)
