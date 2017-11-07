import os
import threading
from flask import (Flask, Response, request, send_file, render_template,
                   redirect, url_for, abort)
from github_webhook import Webhook
from dmsa import ddl, erd, __version__
from dmsa.utility import (get_template_models, get_service_version,
                          get_template_dialects, ReverseProxied, dmsa_version)
import dmsa.cache

PERIODIC_REFRESH_DELAY = 3600  # seconds
POST_HOOK_REFRESH_DELAY = 10

app = Flask('dmsa')
app.wsgi_app = ReverseProxied(app.wsgi_app)
dmsa.cache.set_cache_dir(app.instance_path)

hmac_key = os.environ.get('DMSA_WEBHOOK_SECRET')
webhook = Webhook(app, endpoint='/refresh', secret=hmac_key)


def refresh_data_models_template():
    """Retrieve the data models from the service and cache them"""
    get_template_models(app.config['service'], force_refresh=True)


def refresh_data_models_template_and_reschedule(delay=None):
    """Refresh the data models summary data and optionally reschedule

    Arguments:
        delay - delay in seconds (to reschedule), or None (to not reschedule)
    """
    refresh_data_models_template()
    if delay:
            schedule_data_models_template_refresh(delay, reschedule=True)


def schedule_data_models_template_refresh(delay, reschedule=False):
    """Refresh the data models summary data after a delay in seconds

    Arguments:
        delay - delay in seconds
        reschedule - whether to reschedule another refresh afterwards
    """
    t = threading.Timer(delay,
                        refresh_data_models_template_and_reschedule,
                        args=[delay if reschedule else None]
                        )
    t.start()


@webhook.hook(event_type='push')
def webhook_route(data):
    schedule_data_models_template_refresh(delay=POST_HOOK_REFRESH_DELAY)


@app.route('/')
@dmsa_version
def index_route():
    return render_template('index.html', models=get_template_models(app.config['service']))


@app.route('/<model_name>/')
@dmsa_version
def model_route(model_name):

    for model in get_template_models(app.config['service']):
        if model['name'] == model_name:
            break
    else:
        abort(404)

    return render_template('model.html', model=model)


@app.route('/<model_name>/<version_name>/')
@dmsa_version
def version_route(model_name, version_name):

    for model in get_template_models(app.config['service']):
        if model['name'] == model_name:
            break
    else:
        abort(404)

    for version in model['versions']:
        if version['name'] == version_name:
            break
    else:
        abort(404)

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
        model, version, get_service_version(app.config['service']), __version__,
        ext)
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
    """Serve the file generated by create_erd_route (/<model>/<version>/erd)"""
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


@app.route('/<model>/<version>/nologging/oracle/',
           defaults={'elements': 'all'})
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


def build_app(service, refresh_interval=PERIODIC_REFRESH_DELAY):
    """Builds and returns a web app that exposes DDL and ERD.

    Arguments:
      service - Base URL of the data models service to use.
      refresh_interval - Number of seconds between refreshes of model summaries.
          To disable periodic refreshes, set to None.
    """  # noqa

    app.config['service'] = service
    app.config['dialects'] = get_template_dialects()

    # Cache the data models from the data models service
    # and refresh periodically.
    refresh_data_models_template_and_reschedule(delay=refresh_interval)

    return app
