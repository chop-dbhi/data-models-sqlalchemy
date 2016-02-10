from __future__ import unicode_literals

import os
from sqlalchemy import MetaData
from nose.tools import eq_
from dmsa import make_model_from_service
from dmsa.utility import get_template_models, get_model_json

SERVICE = os.environ.get('DMSA_TEST_SERVICE',
                         'http://data-models.origins.link/')

def test_model_creation():
    for m in get_template_models(SERVICE):
        for v in m['versions']:
            yield check_model_creation, m['name'], v['name'], SERVICE

def check_model_creation(model, model_version, service):

    model_json = get_model_json(model, model_version, service)

    metadata = MetaData()
    metadata = make_model_from_service(model, model_version, service, metadata)

    eq_(len(metadata.tables), len(model_json['tables']) )
