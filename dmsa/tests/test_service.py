import os
from nose.tools import eq_
from dmsa import service
from dmsa.utility import get_template_models

SERVICE = os.environ.get('DMSA_TEST_SERVICE',
                         'https://data-models-service.research.chop.edu/')

app = service.build_app(SERVICE, refresh_interval=None)
app.config['TESTING'] = True
test_app = app.test_client()

ENDPOINTS = ['/']

for m in get_template_models(SERVICE):

    ENDPOINTS.append('/%s/' % m['name'])

    for v in m['versions']:

        ENDPOINTS.append('/%s/%s/' % (m['name'], v['name']))
        ENDPOINTS.append('/%s/%s/erd/' % (m['name'], v['name']))

        ENDPOINTS.append('/%s/%s/ddl/sqlite/' %
                         (m['name'], v['name']))
        ENDPOINTS.append('/%s/%s/drop/sqlite/' %
                         (m['name'], v['name']))
        ENDPOINTS.append('/%s/%s/delete/sqlite/' %
                         (m['name'], v['name']))

        for e in ['tables', 'indexes']:

            ENDPOINTS.append('/%s/%s/ddl/sqlite/%s/' %
                             (m['name'], v['name'], e))
            ENDPOINTS.append('/%s/%s/drop/sqlite/%s/' %
                             (m['name'], v['name'], e))


def test_endpoints():
    for endpoint in ENDPOINTS:
        yield check_endpoint, endpoint


def check_endpoint(endpoint):
    r = test_app.get(endpoint)
    if endpoint.endswith('/erd/'):
        try:
            import eralchemy  # noqa
        except ImportError:
            eq_(r.status_code, 500)
        else:
            eq_(r.status_code, 302)
            # Set endpoint to redirect location stripped of hostname and
            # retest.
            endpoint = r.location[r.location.find('/', 8):]
            r = test_app.get(endpoint)
            eq_(r.status_code, 200)
    else:
        eq_(r.status_code, 200)
