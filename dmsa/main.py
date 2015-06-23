#! /usr/bin/env python

import sys
from dmsa import ddl, erd, service


def main():
    usage = """Data Model DDL and ERD Generator

    Usage: main.py (ddl | erd | start) [<args>...]

    """  # noqa

    from docopt import docopt

    # Ignore command name.
    argv = sys.argv[1:]

    args = docopt(usage, argv=argv, version='0.3', options_first=True)

    # Trim subcommand.
    sub_argv = argv[1:]

    if args['ddl']:
        ddl.main(sub_argv)
    elif args['erd']:
        erd.main(sub_argv)
    elif args['start']:
        service.main(sub_argv)


if __name__ == '__main__':
    main()
