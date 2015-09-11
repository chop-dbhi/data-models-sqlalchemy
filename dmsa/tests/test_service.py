from nose.tools import eq_
from dmsa import service
from dmsa.settings import MODELS

service.app.config['TESTING'] = True
app = service.app.test_client()

ENDPOINTS = ['/']

for m in MODELS:

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

        for e in ['tables', 'constraints', 'indexes']:

            ENDPOINTS.append('/%s/%s/ddl/sqlite/%s/' %
                             (m['name'], v['name'], e))
            ENDPOINTS.append('/%s/%s/drop/sqlite/%s/' %
                             (m['name'], v['name'], e))


def test_endpoints():
    for endpoint in ENDPOINTS:
        yield check_endpoint, endpoint


def check_endpoint(endpoint):
    r = app.get(endpoint)
    if endpoint.endswith('/erd/'):
        eq_(r.status_code, 302)
        # Set endpoint to redirect location stripped of hostname and retest.
        print r.location
        endpoint = r.location[r.location.find('/', 8):]
        r = app.get(endpoint)
        print endpoint, r.status_code, dir(r)
        eq_(r.status_code, 200)
    else:
        eq_(r.status_code, 200)
