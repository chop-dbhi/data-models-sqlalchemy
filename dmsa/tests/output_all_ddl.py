import os
import sys
import requests
from dmsa import ddl, __version__
from dmsa.settings import MODELS, DIALECTS

default_outpath = os.path.join(os.getcwd(),
                               'dmsa_%s_all_ddl.sql' % __version__)
outpath = sys.argv[1] if len(sys.argv) > 1 else default_outpath
baseurl = os.environ.get('DMSA_TEST_CONTAINER_URL', 'http://127.0.0.1:80/')

f = open(outpath, 'w')

for m in MODELS:

    for v in m['versions']:

        #f.write(' '.join(['#', m['name'], v['name'], 'oracle', 'logging\n']))
        #f.write(requests.get(baseurl + '%s/%s/logging/oracle/' % \
        #                     (m['name'], v['name'])).text)

        #f.write(' '.join([m['name'], v['name'], 'oracle', 'nologging\n']))
        #f.write(requests.get(baseurl + '%s/%s/nologging/oracle/' % \
        #                     (m['name'], v['name'])).text)

        for d in DIALECTS:

            f.write(' '.join([m['name'], v['name'], d['name'], 'ddl\n']))
            f.write(requests.get(baseurl + '%s/%s/ddl/%s/' % \
                                 (m['name'], v['name'], d['name'])).text)

            f.write(' '.join([m['name'], v['name'], d['name'], 'drop\n']))
            f.write(requests.get(baseurl + '%s/%s/drop/%s/' % \
                                 (m['name'], v['name'], d['name'])).text)

            f.write(' '.join([m['name'], v['name'], d['name'], 'delete\n']))
            f.write(requests.get(baseurl + '%s/%s/delete/%s/' % \
                                 (m['name'], v['name'], d['name'])).text)

f.close()
