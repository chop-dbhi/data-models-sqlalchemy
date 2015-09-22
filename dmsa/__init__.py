import os

serial = os.environ.get('BUILD_NUM') or '0'
sha = os.environ.get('COMMIT_SHA1') or '0'
sha = sha[0:8]

__version_info__ = {
    'major': 0,
    'minor': 5,
    'micro': 7,
    'releaselevel': 'beta',
    'serial': serial,
    'sha': sha
}


def get_version(short=False):
    assert __version_info__['releaselevel'] in ('alpha', 'beta', 'final')
    vers = ['%(major)i.%(minor)i.%(micro)i' % __version_info__, ]
    if __version_info__['releaselevel'] != 'final' and not short:
        __version_info__['lvlchar'] = __version_info__['releaselevel'][0]
        vers.append('%(lvlchar)s%(serial)s+%(sha)s' % __version_info__)
    return ''.join(vers)

__version__ = get_version()

version_module_code = """
import requests
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from dmsa.settings import get_url
from dmsa.makers import make_model

url = get_url('{name}', '{version}')

model_json = requests.get(url).json()

metadata = MetaData()

make_model(model_json, metadata)

Base = declarative_base(metadata=metadata)

for table in metadata.tables.values():
    cls_name = ''.join(i.capitalize() for i in table.name.split('_'))
    globals()[cls_name] = table
"""


def add_model_modules():

    import sys
    import imp
    from dmsa.settings import MODELS

    for model in MODELS:

        path = 'dmsa.' + model['name']
        module = imp.new_module(path)
        module.__file__ = '(dynamically constructed)'
        module.__dict__['__package__'] = 'dmsa'
        locals()[model['name']] = module
        sys.modules[path] = module

        for version in model['versions']:

            version_name = 'v' + version['name'].replace('.', '_')
            version_path = path + '.' + version_name
            version_module = imp.new_module(version_path)
            version_module.__file__ = '(dynamically constructed)'
            version_module.__dict__['__package__'] = 'dmsa'
            setattr(module, version_name, version_module)
            sys.modules[version_path] = version_module

            models_path = version_path + '.models'
            models_module = imp.new_module(models_path)
            models_module.__file__ = '(dynamically constructed)'
            models_module.__dict__['__package__'] = 'dmsa'
            setattr(version_module, 'models', models_module)

            code = version_module_code.format(name=model['name'],
                                              version=version['name'])

            exec(code, models_module.__dict__)
            sys.modules[models_path] = models_module
