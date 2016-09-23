import os
from nose import SkipTest
from nose.tools import ok_
from dmsa import erd

# This testing function is definitely non-exhaustive. It operates on the
# OMOP v5.0.0 data model, retrieved from the default data-models-service URL
# (see dmsa.settings; in CircleCI, this is set to localhost and a dms is
# started locally). Additionally, the test does not check anything about the
# output ERD, merely that the functions run without error and produce a file at
# the output location.

SERVICE = os.environ.get('DMSA_TEST_SERVICE',
                         'https://data-models-service.research.chop.edu/')


def test_all():
    try:
        erd.write('omop', '5.0.0', 'test_erd_out.png', SERVICE)
    except ImportError:
        raise SkipTest('Skipping erd test; ERLAlchemy package not installed')
    ok_(os.path.exists('test_erd_out.png'))
