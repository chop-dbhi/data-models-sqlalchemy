import os

URL_TEMPLATE = os.environ.get('URL_TEMPLATE') or \
    'http://data-models.origins.link/schemata/{model}/{version}?format=json'

OMOP_V4_URL = os.environ.get('OMOP_V4_URL') or \
    URL_TEMPLATE.format(model='omop', version='v4')

OMOP_V5_URL = os.environ.get('OMOP_V5_URL') or \
    URL_TEMPLATE.format(model='omop', version='v5')

PEDSNET_V1_URL = os.environ.get('PEDSNET_V1_URL') or \
    URL_TEMPLATE.format(model='pedsnet', version='v1')

PEDSNET_V2_URL = os.environ.get('PEDSNET_V2_URL') or \
    URL_TEMPLATE.format(model='pedsnet', version='v2')

PCORNET_V1_URL = os.environ.get('PCORNET_V1_URL') or \
    URL_TEMPLATE.format(model='pcornet', version='v1')

PCORNET_V2_URL = os.environ.get('PCORNET_V2_URL') or \
    URL_TEMPLATE.format(model='pcornet', version='v2')

PCORNET_V3_URL = os.environ.get('PCORNET_V3_URL') or \
    URL_TEMPLATE.format(model='pcornet', version='v3')

I2B2_V1_7_URL = os.environ.get('I2B2_V1_7_URL') or \
    URL_TEMPLATE.format(model='i2b2', version='v1.7')

I2B2_PEDSNET_V2_URL = os.environ.get('I2B2_PEDSNET_V2_URL') or \
    URL_TEMPLATE.format(model='i2b2_pedsnet', version='v2')

MODELS = [
    {
        'pretty': 'PEDSnet',
        'name': 'pedsnet',
        'versions': [
            {
                'name': 'v2',
                'url': PEDSNET_V2_URL
            },
            {
                'name': 'v1',
                'url': PEDSNET_V1_URL
            }
        ]
    },
    {
        'pretty': 'i2b2 PEDSnet',
        'name': 'i2b2_pedsnet',
        'versions': [
            {
                'name': 'v2',
                'url': I2B2_PEDSNET_V2_URL
            }
        ]
    },
    {
        'pretty': 'PCORnet',
        'name': 'pcornet',
        'versions': [
            {
                'name': 'v3',
                'url': PCORNET_V3_URL
            },
            {
                'name': 'v2',
                'url': PCORNET_V2_URL
            },
            {
                'name': 'v1',
                'url': PCORNET_V1_URL
            }
        ]
    },
    {
        'pretty': 'OMOP',
        'name': 'omop',
        'versions': [
            {
                'name': 'v5',
                'url': OMOP_V5_URL
            },
            {
                'name': 'v4',
                'url': OMOP_V4_URL
            }
        ]
    },
    {
        'pretty': 'i2b2',
        'name': 'i2b2',
        'versions': [
            {
                'name': 'v1.7',
                'url': I2B2_V1_7_URL
            }
        ]
    }
]

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


def get_url(model, version):

    for m in MODELS:
        if m['name'] == model:
            for v in m['versions']:
                if v['name'] == version:
                    return v['url']
