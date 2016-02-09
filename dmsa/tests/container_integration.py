import os
import docker
import requests
from requests.exceptions import ConnectionError
from unittest.case import SkipTest
from nose.tools import eq_
from dmsa.utility import get_template_models, get_template_dialects

DMSA_AVAILABLE = False
docker_client = docker.Client(base_url='unix://var/run/docker.sock',
                              version='auto')

try:
    containers = docker_client.containers(filters={'status': 'running'})
except ConnectionError:
    containers = []
    raise SkipTest('Docker daemon socket not found.')

for container in containers:
    if 'dbhi/data-models-sqlalchemy' in container['Image']:
        DMSA_AVAILABLE = True

ENDPOINTS = ['']

for m in get_template_models(os.environ.get('DMSA_TEST_SERVICE') or \
                             'http://data-models.origins.link/'):

    ENDPOINTS.append('%s/' % m['name'])

    for v in m['versions']:

        ENDPOINTS.append('%s/%s/' % (m['name'], v['name']))
        ENDPOINTS.append('%s/%s/erd/' % (m['name'], v['name']))

        ENDPOINTS.append('%s/%s/logging/oracle/' %
                         (m['name'], v['name']))
        ENDPOINTS.append('%s/%s/nologging/oracle/' %
                         (m['name'], v['name']))

        for d in get_template_dialects():

            ENDPOINTS.append('%s/%s/ddl/%s/' %
                             (m['name'], v['name'], d['name']))
            ENDPOINTS.append('%s/%s/drop/%s/' %
                             (m['name'], v['name'], d['name']))
            ENDPOINTS.append('%s/%s/delete/%s/' %
                             (m['name'], v['name'], d['name']))

            for e in ['tables', 'constraints', 'indexes']:

                ENDPOINTS.append('%s/%s/ddl/%s/%s/' %
                                 (m['name'], v['name'], d['name'], e))
                ENDPOINTS.append('%s/%s/drop/%s/%s/' %
                                 (m['name'], v['name'], d['name'], e))

                if e != 'constraints' and d['name'] == 'oracle':
                    ENDPOINTS.append('%s/%s/logging/oracle/%s/' %
                                     (m['name'], v['name'], e))
                    ENDPOINTS.append('%s/%s/nologging/oracle/%s/' %
                                     (m['name'], v['name'], e))


def test_container_endpoints():
    if not DMSA_AVAILABLE:
        raise SkipTest('Running dbhi/data-models-sqlalchemy container not ' +
                       'found.')
    for endpoint in ENDPOINTS:
        yield check_container_endpoint, endpoint


def check_container_endpoint(endpoint):
    # Unlike in the test_service flask testing app instance, the requests.get
    # function follows redirects automatically and will report the final
    # status code, so this works even for the erd endpoints.
    r = requests.get(os.environ.get('DMSA_TEST_CONTAINER_URL',
                                    'http://127.0.0.1:80/') + endpoint)
    eq_(r.status_code, 200)
