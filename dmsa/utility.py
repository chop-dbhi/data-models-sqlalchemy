import requests
from functools import wraps
from flask import make_response
from dmsa import __version__
from dmsa.models import (get_cached_template_models, set_cached_template_models)

PRETTY_MODELS = {
    'i2b2': 'i2b2',
    'i2b2_pedsnet': 'i2b2 for PEDSnet',
    'omop': 'OMOP',
    'pcornet': 'PCORnet',
    'pedsnet': 'PEDSnet'
}

PRETTY_DIALECTS = {
    'postgresql': 'PostgreSQL',
    'oracle': 'Oracle',
    'mssql': 'MS SQL Server',
    'mysql': 'MySQL',
    'sqlite': 'SQLite'
}

RELEASE_COLORS = {
    'alpha': 'red',
    'beta': 'orange',
    'final': ''
}


def get_model_json(model, model_version, service):
    """Retrieve model JSON for the model and version from the service."""
    r = requests.get(''.join([service, 'schemata/', model, '/', model_version,
                              '?format=json']))
    return r.json()


def get_service_version(service):
    """Retrieve version of the specified service."""
    r = requests.get(service)
    return r.headers['User-Agent'].split(' ')[0].split('/')[1]


def get_models_json(service):
    """Retrieve the models and their versions from the service."""
    r = requests.get(service + 'models?format=json')
    return r.json()


def get_template_models(service, force_refresh=False):

    if not force_refresh:
        models = get_cached_template_models()
        if models:
            return models

    models = []
    svc_models = get_models_json(service)

    for svc_model in svc_models:
        for model in models:
            if model['name'] == svc_model['name']:
                model['versions'].append({
                    'name': svc_model['version'],
                    'release_level': svc_model['release']['level'],
                    'release_color':
                        RELEASE_COLORS[svc_model['release']['level']]
                })
                break
        else:
            models.append({
                'pretty': PRETTY_MODELS.get(svc_model['name'],
                                            svc_model['name']),
                'name': svc_model['name'],
                'versions': [{
                    'name': svc_model['version'],
                    'release_level': svc_model['release']['level'],
                    'release_color':
                        RELEASE_COLORS[svc_model['release']['level']]
                }]
            })

    for model in models:
        model['versions'] = sorted(model['versions'], key=lambda k: k['name'])

    sorted_models = sorted(models, key=lambda k: k['pretty'].lower())
    set_cached_template_models(sorted_models)

    return sorted_models


def get_template_dialects():
    dialects = []
    for k, v in PRETTY_DIALECTS.iteritems():
        dialects.append({
            'name': k,
            'pretty': v
        })
    return sorted(dialects, key=lambda k: k['pretty'])


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


class ReverseProxied(object):
    '''Wrap the application in this middleware and configure the
    front-end server to add these headers, to let you quietly bind
    this to a URL other than / and to an HTTP scheme that is
    different than what is used locally.

    In nginx:
    location /myprefix {
        proxy_pass http://192.168.0.1:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Scheme $scheme;
        proxy_set_header X-Script-Name /myprefix;
        }

    :param app: the WSGI application
    '''
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]

        scheme = environ.get('HTTP_X_SCHEME', '')
        if scheme:
            environ['wsgi.url_scheme'] = scheme

        server = environ.get('HTTP_X_FORWARDED_SERVER', '')
        if server:
            environ['HTTP_HOST'] = server

        return self.app(environ, start_response)
