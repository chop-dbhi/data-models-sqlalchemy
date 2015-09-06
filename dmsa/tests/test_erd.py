import os.path
from nose.tools import ok_
from dmsa import erd

# This testing function is definitely non-exhaustive. It operates on the
# OMOP v5.0.0 data model, retrieved from the default data-models-service URL
# (see dmsa.settings; in CircleCI, this is set to localhost and a dms is
# started locally). Additionally, the test does not check anything about the
# output ERD, merely that the functions run without error and produce a file at
# the output location.


def test_all():
    erd.main(['omop', '5.0.0', 'test_erd_out.png'])
    ok_(os.path.exists('test_erd_out.png'))
