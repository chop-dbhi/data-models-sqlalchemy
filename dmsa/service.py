#!/usr/bin/env python

import os
import sys
from flask import Flask, Response, request, send_file
from dmsa.ddl import main as ddl
from dmsa.erd import main as erd

app = Flask('dmsa')


@app.route('/<model>/<version>/ddl/<dialect>/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/ddl/<dialect>/<elements>/')
def ddl_route(model, version, dialect, elements):

    args = []

    if elements == 'tables':
        args.extend(['-c', '-i'])

    if elements == 'constraints':
        args.extend(['-t', '-i'])

    if elements == 'indexes':
        args.extend(['-t', '-c'])

    args.extend(['-r', model, version, dialect])
    ddl_str = ddl(args)

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/erd/')
def erd_route(model, version):

    ext = request.args.get('format') or 'png'

    filename = '%s_%s.%s' % (model, version, ext)

    try:
        os.mkdir('static')
    except OSError:
        pass

    erd([model, version, 'static/' + filename])

    return send_file('static/' + filename)


def main(argv=None):
    usage = """Data Model DDL and ERD Web Service

    Exposes generated DDL and ERD at HTTP endpoints.

    Usage: service.py [options]

    Options:

        -h --help       Show this screen.
        --host=HOST     The hostname to listen on [default: 127.0.0.1].
        --port=PORT     The port of the webserver [default: 5000].
        --debug         Enable debug mode.

    """  # noqa

    from docopt import docopt

    # Ignore command name if called from command line.
    if argv is None:
        argv = sys.argv[1:]

    args = docopt(usage, argv=argv, version='0.3')

    app.run(host=args['--host'], port=args['--port'], debug=args['--debug'])


if __name__ == '__main__':
    main()
