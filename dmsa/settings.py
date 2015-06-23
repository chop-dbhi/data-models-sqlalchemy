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

model_urls = {
    'omop': {
        'v4': OMOP_V4_URL,
        'v5': OMOP_V5_URL
    },
    'pedsnet': {
        'v1': PEDSNET_V1_URL,
        'v2': PEDSNET_V2_URL
    },
    'pcornet': {
        'v1': PCORNET_V1_URL,
        'v2': PCORNET_V2_URL,
        'v3': PCORNET_V3_URL
    },
    'i2b2': {
        'v1.7': I2B2_V1_7_URL
    },
    'i2b2_pedsnet': {
        'v2': I2B2_PEDSNET_V2_URL
    }
}


def get_url(model, version):
    return model_urls[model][version]
