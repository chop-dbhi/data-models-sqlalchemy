import sys
import requests
from eralchemy import render_er
from sqlalchemy import MetaData
from dmsa import __version__
from dmsa.settings import get_url
from dmsa.makers import make_model


def main(argv=None):
    usage = """Data Model ERD Generator

    Generates an entity relationship diagram for the data model specified. If
    passing a custom URL, the data model returned must be in the JSON format
    defined by the chop-dbhi/data-models package. The generated diagram is
    saved to the named output file.

    Usage: erd.py [options] <model> <version> <outfile>

    Options:
        -h --help            Show this screen.
        -u URL --url=URL     Retrieve model JSON from this URL instead of the
                             default or environment-variable-passed URL.

    """  # noqa

    from docopt import docopt

    # Ignore command name if called from command line.
    argv = argv or sys.argv[1:]

    args = docopt(usage, argv=argv, version=__version__)

    url = args['--url'] or get_url(args['<model>'], args['<version>'])
    model_json = requests.get(url).json()

    metadata = MetaData()
    make_model(model_json, metadata)

    render_er(metadata, args['<outfile>'])


if __name__ == '__main__':
    main()
