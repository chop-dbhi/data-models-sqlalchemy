import sys
from setuptools import setup, find_packages

if sys.version_info < (2, 7):
    raise EnvironmentError('Python 2.7.x is required')

with open('README.md', 'r') as f:
    long_description = f.read()

install_requires = [
    'SQLAlchemy==1.0.5',
    'ERAlchemy==0.0.28',
    'docopt==0.6.2'
]

kwargs = {
    'name': 'dmsa',
    'version': '0.2',
    'author': 'The Children\'s Hospital of Philadelphia',
    'author_email': 'cbmisupport@email.chop.edu',
    'url': 'https://github.com/chop-dbhi/data-models-sqlalchemy',
    'description': ('Scripts to create SQLAlchemy models, DDL, and ER '
                    'diagrams from JSON data models produced by '
                    'chop-dbhi/data-models.'),
    'long_description': long_description,
    'packages': find_packages(),
    'install_requires': install_requires,
    'download_url': 'https://github.com/chop-dbhi/data-models/tarball/0.2',
}

setup(**kwargs)
