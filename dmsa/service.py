import os
import sys
from flask import (Flask, Response, request, send_file, render_template,
                   redirect, url_for)
from dmsa import ddl, erd, __version__
from dmsa.utility import (PRETTY_MODELS, PRETTY_DIALECTS, get_model_json,
                          get_service_version, get_template_models,
                          get_template_dialects, ReverseProxied, dmsa_version)

app = Flask('dmsa')
app.wsgi_app = ReverseProxied(app.wsgi_app)

@app.route('/')
@dmsa_version
def index_route():
    return render_template('index.html', models=app.config['models'])


@app.route('/<model_name>/')
@dmsa_version
def model_route(model_name):

    for model in app.config['models']:
        if model['name'] == model_name:
            break

    return render_template('model.html', model=model)


@app.route('/<model_name>/<version_name>/')
@dmsa_version
def version_route(model_name, version_name):

    for model in app.config['models']:
        if model['name'] == model_name:
            break

    for version in model['versions']:
        if version['name'] == version_name:
            break

    return render_template('version.html', model=model, version=version,
                           dialects=app.config['dialects'])


@app.route('/<model>/<version>/ddl/<dialect>/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/ddl/<dialect>/<elements>/')
@dmsa_version
def ddl_route(model, version, dialect, elements):

    tables, constraints, indexes = False, False, False

    if elements in ['tables', 'all']:
        tables = True

    if elements in ['constraints', 'all']:
        constraints = True

    if elements in ['indexes', 'all']:
        indexes = True

    ddl_str = ddl.generate(model, version, dialect, tables=tables,
                           constraints=constraints, indexes=indexes,
                           service=app.config['service'])

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/drop/<dialect>/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/drop/<dialect>/<elements>/')
@dmsa_version
def drop_route(model, version, dialect, elements):

    tables, constraints, indexes = False, False, False

    if elements in ['tables', 'all']:
        tables = True

    if elements in ['constraints', 'all']:
        constraints = True

    if elements in ['indexes', 'all']:
        indexes = True

    ddl_str = ddl.generate(model, version, dialect, tables=tables,
                           constraints=constraints, indexes=indexes,
                           drop=True, service=app.config['service'])

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/delete/<dialect>/')
@dmsa_version
def delete_route(model, version, dialect):

    ddl_str = ddl.generate(model, version, dialect, delete_data=True,
                           service=app.config['service'])

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/erd/')
@dmsa_version
def create_erd_route(model, version):

    ext = request.args.get('format') or 'png'

    filename = '{0}_{1}_dms_{2}_dmsa_{3}.{4}'.format(
        model, version, app.config['service_version'], __version__, ext)
    filepath = '/'.join([app.instance_path, filename])

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        erd.write(model, version, filepath, app.config['service'])
    except ImportError:
        return render_template('erd_500.html'), 500

    return redirect(url_for('erd_route', model=model, version=version,
                            filename=filename))


@app.route('/<model>/<version>/erd/<filename>')
@dmsa_version
def erd_route(model, version, filename):

    filepath = '/'.join([app.instance_path, filename])

    return send_file(filepath)


@app.route('/<model>/<version>/logging/oracle/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/logging/oracle/<elements>/')
@dmsa_version
def logging_route(model, version, elements):

    tables, constraints, indexes = False, False, False

    if elements in ['tables', 'all']:
        tables = True

    if elements in ['constraints', 'all']:
        constraints = True

    if elements in ['indexes', 'all']:
        indexes = True

    ddl_str = ddl.generate(model, version, 'oracle', tables=tables,
                           constraints=constraints, indexes=indexes,
                           logging=True, service=app.config['service'])

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


@app.route('/<model>/<version>/nologging/oracle/', defaults={'elements': 'all'})
@app.route('/<model>/<version>/nologging/oracle/<elements>/')
@dmsa_version
def nologging_route(model, version, elements):

    tables, constraints, indexes = False, False, False

    if elements in ['tables', 'all']:
        tables = True

    if elements in ['constraints', 'all']:
        constraints = True

    if elements in ['indexes', 'all']:
        indexes = True

    ddl_str = ddl.generate(model, version, 'oracle', tables=tables,
                           constraints=constraints, indexes=indexes,
                           nologging=True, service=app.config['service'])

    resp = Response(ddl_str, status='200 OK', mimetype='text/plain')

    return resp


def build_app(service):
    """Builds and returns a web app that exposes DDL and ERD.

    Arguments:
      service  Base URL of the data models service to use.
    """  # noqa

    app.config['service'] = service
    app.config['service_version'] = get_service_version(service)
    app.config['models'] = get_template_models(service)
    app.config['dialects'] = get_template_dialects()

    return app


if __name__ == '__main__':
    main()
