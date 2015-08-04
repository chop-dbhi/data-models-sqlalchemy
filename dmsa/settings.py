import os
import requests

URL_TEMPLATE = os.environ.get('URL_TEMPLATE') or \
    'http://data-models.origins.link/schemata/{model}/{version}?format=json'

MODELS_URL = os.environ.get('MODELS_URL') or \
    'http://data-models.origins.link/models?format=json'

PRETTY_MODEL_NAMES = {
    'i2b2': 'i2b2',
    'i2b2_pedsnet': 'i2b2 PEDSnet',
    'omop': 'OMOP',
    'pcornet': 'PCORnet',
    'pedsnet': 'PEDSnet'
}

DIALECTS = [
    {
        'pretty': 'PostgreSQL',
        'name': 'postgresql'
    },
    {
        'pretty': 'Oracle',
        'name': 'oracle'
    },
    {
        'pretty': 'MS SQL Server',
        'name': 'mssql'
    },
    {
        'pretty': 'MySQL',
        'name': 'mysql'
    }
]

models_json = requests.get(MODELS_URL).json()

MODELS = []

for model in models_json:

    for model_store in MODELS:

        if model_store['name'] == model['name']:

            model_store['versions'].append({
                'name': model['version'],
                'url': URL_TEMPLATE.format(model=model['name'],
                                           version=model['version'])
            })

            break
    else:

        MODELS.append({
            'pretty': PRETTY_MODEL_NAMES.get(model['name'], model['name']),
            'name': model['name'],
            'versions': [
                {
                    'name': model['version'],
                    'url': URL_TEMPLATE.format(model=model['name'],
                                               version=model['version'])
                }
            ]
        })


def get_url(model, version):

    for m in MODELS:
        if m['name'] == model:
            for v in m['versions']:
                if v['name'] == version:
                    return v['url']
