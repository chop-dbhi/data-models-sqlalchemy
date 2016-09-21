from sqlalchemy import MetaData
from dmsa.utility import get_model_json
from dmsa.makers import make_model


def write(model, model_version, output, service):
    """Generate entity relationship diagram for the data model specified.

    Arguments:
      model          Model to generate DDL for.
      model_version  Model version to generate DDL for.
      output         Output file for ERD.
      service        Base URL of the data models service to use.

    Raises:
        ImportError, if erlalchemy cannot be imported
    """  # noqa

    metadata = MetaData()
    model_json = get_model_json(model, model_version, service)
    make_model(model_json, metadata)

    from eralchemy import render_er

    render_er(metadata, output)


if __name__ == '__main__':
    main()
