import json
from urllib import urlopen
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from dmsa.settings import get_url
from dmsa.makers import make_model

url = get_url('omop', 'v4')

model_json = json.loads(urlopen(url).read())

metadata = MetaData()

make_model(model_json, metadata)

Base = declarative_base(metadata=metadata)

for table in metadata.tables.values():
    cls_name = ''.join(i.capitalize() for i in table.name.split('_'))
    globals()[cls_name] = table
