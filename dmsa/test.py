import sys
import requests
from dmsa import __version__
from dmsa.settings import MODELS, DIALECTS


def main(argv=None):
    usage = """Integration Tests for Web Service

    Tests each endpoint of the data model DDL and ERD web service to ensure it
    returns a status code of 200. If a test fails and the server is in debug
    mode, finding and printing the traceback is attempted. The URL defaults to
    http://127.0.0.1:5000

    Usage: test.py [options] [<url>]

    Options:
        -h --help           Show this screen.

    """

    from docopt import docopt

    # Ignore command name if called from command line.
    if argv is None:
        argv = sys.argv[1:]

    args = docopt(usage, argv=argv, version=__version__)

    endpoints = ['/']

    for m in MODELS:

        endpoints.append('/%s/' % m['name'])

        for v in m['versions']:

            endpoints.append('/%s/%s/' % (m['name'], v['name']))
            endpoints.append('/%s/%s/ddl/' % (m['name'], v['name']))
            endpoints.append('/%s/%s/erd/' % (m['name'], v['name']))

            for d in DIALECTS:

                endpoints.append('/%s/%s/ddl/%s/' % (m['name'], v['name'],
                                                     d['name']))

                for e in ['tables', 'constraints', 'indexes']:

                    endpoints.append('/%s/%s/ddl/%s/%s/' %
                                     (m['name'], v['name'], d['name'], e))

    err_num = 0

    err_urls = []

    for endpoint in endpoints:

        url = args['<url>'] or 'http://127.0.0.1:5000' + endpoint

        r = requests.get(url)

        try:
            assert r.status_code == 200
        except AssertionError:

            err_num += 1

            err_urls.append(url)

            print('Failed URL: %s\n' % url)

            tb_loc = r.text.rfind('Traceback')

            if tb_loc != -1:

                print(r.text[tb_loc:].rstrip('-->\n') + '\n\n')

    if err_num > 0:

        raise AssertionError('%d Failed URLs:\n    %s' %
                             (err_num, ',\n    '.join(err_urls)))

if __name__ == '__main__':
    main()
