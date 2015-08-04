import os
import sys
from functools import wraps
from flask import (Flask, Response, request, send_file, render_template,
                   redirect, url_for, make_response)
from dmsa import ddl, erd, __version__
from dmsa.settings import MODELS, DIALECTS, DMS_VERSION

app = Flask('dmsa')


def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def dmsa_version(f):
    """This decorator passes User-Agent: DMSA/<version>
    (+https://github.com/chop-dbhi/data-models-sqlalchemy)"""
    return add_response_headers(
        {'User-Agent':
         'DMSA/{0} (+https://github.com/chop-dbhi/data-models-sqlalchemy)'.
         format(__version__)})(f)


@app.route('/')
@dmsa_version
def index_route():
    return render_template('index.html', models=MODELS)


@app.route('/<model_name>/')
@dmsa_version
def model_route(model_name):

    for model in MODELS:
        if model['name'] == model_name:
            break

    return render_template('model.html', model=model)


@app.route('/<model_name>/<version_name>/')
@dmsa_version
def version_route(model_name, version_name):

    for model in MODELS:
        if model['name'] == model_name:
            break

    for version in model['versions']:
        if version['name'] == version_name:
            break

    return render_template('version.html', model=model, version=version,
                           dialects=DIALECTS)


@app.route('/<model>/<version>/ddl/<dialect>/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/ddl/<dialect>/<elements>/')
@dmsa_version
def ddl_route(model, version, dialect, elements):

    args = []

    if elements == 'tables':
        args.extend(['-c', '-i'])

    if elements == 'constraints':
        args.extend(['-t', '-i'])

    if elements == 'indexes':
        args.extend(['-t', '-c'])

    args.extend(['-r', model, version, dialect])
    ddl_str = ddl.main(args)

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/drop/<dialect>/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/drop/<dialect>/<elements>/')
@dmsa_version
def drop_route(model, version, dialect, elements):

    args = []

    if elements == 'tables':
        args.extend(['-c', '-i'])

    if elements == 'constraints':
        args.extend(['-t', '-i'])

    if elements == 'indexes':
        args.extend(['-t', '-c'])

    args.extend(['-r', '-d', model, version, dialect])
    ddl_str = ddl.main(args)

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/delete/<dialect>/')
@dmsa_version
def delete_route(model, version, dialect):

    args = ['-r', '-x', model, version, dialect]
    ddl_str = ddl.main(args)

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/erd/')
@dmsa_version
def create_erd_route(model, version):

    ext = request.args.get('format') or 'png'

    filename = '{0}_{1}_dms_{2}_dmsa_{3}.{4}'.format(
        model, version, DMS_VERSION, __version__, ext)
    filepath = '/'.join([app.instance_path, filename])

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    erd.main([model, version, filepath])

    return redirect(url_for('erd_route', model=model, version=version,
                            filename=filename))


@app.route('/<model>/<version>/erd/<filename>')
@dmsa_version
def erd_route(model, version, filename):

    filepath = '/'.join([app.instance_path, filename])

    return send_file(filepath)


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

    args = docopt(usage, argv=argv, version=__version__)

    app.run(host=args['--host'], port=int(args['--port']),
            debug=args['--debug'])


if __name__ == '__main__':
    main()
