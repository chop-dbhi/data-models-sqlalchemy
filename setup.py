import sys
from setuptools import setup, find_packages
from dmsa import __version__

if sys.version_info < (2, 7) or sys.version_info > (3, 0):
    raise EnvironmentError('Python 2.7.x is required')

with open('README.md', 'r') as f:
    long_description = f.read()

install_requires = [
    'SQLAlchemy==1.0.5',
    'ERAlchemy==0.0.28',
    'Flask==0.10.1',
    'docopt==0.6.2',
    'requests==2.7.0'
]

kwargs = {
    'name': 'dmsa',
    'version': __version__.replace('-', '', 1),
    'author': 'The Children\'s Hospital of Philadelphia',
    'author_email': 'cbmisupport@email.chop.edu',
    'url': 'https://github.com/chop-dbhi/data-models-sqlalchemy',
    'description': ('SQLAlchemy models and DDL and ERD generation from '
                    'chop-dbhi/data-models style JSON endpoints.'),
    'long_description': long_description,
    'license': 'Other/Proprietary',
    'packages': find_packages(),
    'package_data': {'dmsa': ['templates/*']},
    'install_requires': install_requires,
    'download_url': ('https://github.com/chop-dbhi/'
                     'data-models-sqlalchemy/tarball/%s' % __version__),
    'keywords': ['healthcare', 'data models', 'SQLAlchemy', 'DDL', 'ERD'],
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Healthcare Industry',
        'License :: Other/Proprietary License',
        'Topic :: Database',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Code Generators',
        'Natural Language :: English'
    ],
    'entry_points': {
        'console_scripts': [
            'dmsa = dmsa.main:main'
        ]
    }
}

setup(**kwargs)
