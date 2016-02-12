"""Data Model DDL and ERD Generator with Web Service

Functionality:
  Generates DDL for any data model version stored in chop-dbhi/data-models
  using JSON retrieved from chop-dbhi/data-models-service. Uses the same data
  sources to generate ERDs. Serves both through a basic web service.

Usage:
  dmsa ddl [--service=URL] [-tci] [-d | -x | -n | -l] [-o FILE] <model> <model_version> <dialect>
  dmsa erd [--service=URL] -o FILE <model> <model_version>
  dmsa serve [--service=URL] [--host=HOSTNAME --port=PORT --debug]
  dmsa (-h | --help)
  dmsa --version

Options:
  -h --help            Show this usage message.
  --version            Show version.
  -t --tables          Include tables when generating DDL.
  -c --constraints     Include constraints when generating DDL.
  -i --indexes         Include indexes when generating DDL.
  -d --drop            Generate DDL to drop, instead of create, objects.
  -x --delete-data     Generate DML to delete data from the model.
  -n --nologging       Generate Oracle DDL to make objects "nologging".
  -l --logging         Generate Oracle DDL to make objects "logging".
  -o --output=FILE     Output file for DDL or ERD.
  --host=HOSTNAME      The web service hostname [default: 127.0.0.1].
  --port=PORT          The web service port to listen on [default: 5000].
  --debug              Enable debug mode in the web service.
  --service=URL        Base URL of the data models service to use
                       [default: http://data-models.origins.link/].

"""


def main():
    import sys
    from docopt import docopt
    from dmsa import __version__

    # Parse command line arguments.
    args = docopt(__doc__, argv=sys.argv[1:], version=__version__)

    if args['ddl']:
        from dmsa import ddl

        output = ddl.generate(args['<model>'], args['<model_version>'],
                              args['<dialect>'], args['--tables'],
                              args['--constraints'], args['--indexes'],
                              args['--drop'], args['--delete-data'],
                              args['--nologging'], args['--logging'],
                              args['--service'])

        if args['--output']:
            f = open(args['--output'], 'w')
            f.write(output)
            f.close()
        else:
            return sys.stdout.write(output)

    elif args['erd']:
        from dmsa import erd
        return erd.write(args['<model>'], args['<model_version>'],
                         args['--service'], args['--output'])

    elif args['serve']:
        from dmsa import service
        app = service.build_app(args['--service'])
        app.run(host=args['--host'], port=int(args['--port']),
                debug=args['--debug'])


if __name__ == '__main__':
    main()
