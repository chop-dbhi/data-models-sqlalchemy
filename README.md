# Data Models SQLAlchemy

[![Circle CI](https://circleci.com/gh/chop-dbhi/data-models-sqlalchemy/tree/master.svg?style=svg)](https://circleci.com/gh/chop-dbhi/data-models-sqlalchemy/tree/master) [![Coverage Status](https://coveralls.io/repos/chop-dbhi/data-models-sqlalchemy/badge.svg?branch=master&service=github)](https://coveralls.io/github/chop-dbhi/data-models-sqlalchemy?branch=master)

SQLAlchemy models and DDL and ERD generation for [chop-dbhi/data-models-service](https://github.com/chop-dbhi/data-models-service) style JSON endpoints.

Web service available at http://dmsa.a0b.io/

## SQLAlchemy Models

In your shell, hopefully within a virtualenv:

```sh
pip install dmsa
```

In python:

```python
from sqlalchemy import MetaData
from dmsa import make_model_from_service

metadata = MetaData()
metadata = make_model_from_service('omop', '5.0.0',
                                   'https://data-models-service.research.chop.edu/',
                                   metadata)

for tbl in metadata.sorted_tables:
    print tbl.name
```

These models are dynamically generated at runtime from JSON endpoints provided by chop-dbhi/data-models-service, which reads data stored in chop-dbhi/data-models. Any data model stored there can be converted into SQLAlchemy models. At the time of writing, the following are available.

CAVEAT: The models are currently "Classical"-style and therefore un-mapped. See more information [here](https://github.com/chop-dbhi/data-models-sqlalchemy/issues/22).

- i2b2
    - 1.7.0
- i2b2 for PEDSnet
    - 2.0.1
- OMOP
    - 4.0.0
    - 5.0.0
- PCORnet
    - 1.0.0
    - 2.0.0
    - 3.0.0
- PEDSnet
    - 1.0.0
    - 2.0.0
    - 2.1.0
    - 2.2.0

## DDL and ERD Generation

Entity Relationship Diagram generation requires the optional ERAlchemy package. This is included by the Dockerfile but not by the `dmsa` Python package.

Use of the included Dockerfile is highly recommended to avoid installing DBMS and graphing specific system requirements.

The following DBMS dialects are supported when generating DDL:

- PostgreSQL
- MySQL
- MS SQL Server
- Oracle

### With Docker:

Retrieve the image:

```sh
docker pull dbhi/data-models-sqlalchemy
```

Usage Message:

```sh
docker run --rm dbhi/data-models-sqlalchemy dmsa -h
```

Generate OMOP V5 creation DDL for Oracle:

```sh
docker run --rm dbhi/data-models-sqlalchemy dmsa ddl -tci omop 5.0.0 oracle
```

Generate OMOP V5 drop DDL for Oracle:

```sh
docker run --rm dbhi/data-models-sqlalchemy dmsa ddl -tci --drop omop 5.0.0 oracle
```

Generate OMOP V5 data deletion DML for Oracle:

```sh
docker run --rm dbhi/data-models-sqlalchemy dmsa ddl --delete-data omop 5.0.0 oracle
```

Generate i2b2 PEDSnet V2 ERD (the image will land at `./erd/i2b2_pedsnet_2.0.0_erd.png`):

```sh
docker run --rm -v $(pwd)/erd:/erd dbhi/data-models-sqlalchemy dmsa erd -o /erd/i2b2_pedsnet_2.0.0_erd.png i2b2_pedsnet 2.0.0
```

The `graphviz` graphing package supports a number of other output formats, which are interpreted from the passed extension.

### Without Docker:

Install the system requirements (see Dockerfile for details):

- Python 2.7
- `graphviz` for ERD generation
- Oracle `instantclient-basic` and `-sdk` and `libaio1` for Oracle DDL generation
- `libpq-dev` for PostgreSQL DDL generation
- `unixodbc-dev` for MS SQL Server DDL generation

Install the python requirements, hopefully within a virtualenv (see Dockerfile for details):

```sh
pip install cx-Oracle            # for Oracle DDL generation
pip install psycopg2             # for PostgreSQL DDL generation
pip install PyMySQL              # for MySQL DDL generation
pip install pyodbc               # for MS SQL Server DDL generation
pip install ERAlchemy==0.0.28    # OPTIONAL; only if you need to make ERDs
```

Install the data-models-sqlalchemy python package:

```sh
pip install dmsa
```

Usage Message:

```sh
dmsa -h
```

Generate OMOP V5 creation DDL for Oracle:

```sh
dmsa ddl -tci omop 5.0.0 oracle
```

Generate OMOP V5 drop DDL for Oracle:

```sh
dmsa ddl -tci --drop omop 5.0.0 oracle
```

Generate OMOP V5 data deletion DML for Oracle:

```sh
dmsa ddl --delete-data omop 5.0.0 oracle
```

Generate i2b2 PEDSnet V2 ERD (the image will land at `./erd/i2b2_pedsnet_2.0.0_erd.png`):

```sh
mkdir -p erd
dmsa erd -o ./erd/i2b2_pedsnet_2.0.0_erd.png i2b2_pedsnet 2.0.0
```

## Web Service

The web service uses a [Gunicorn](http://gunicorn.org/) server in the Docker container and the Flask debug server locally. It exposes the following endpoints:

- Creation DDL at `/<model>/<version>/ddl/<dialect>/`
- Creation DDL for only `table`, `constraint`, or `index` elements at `/<model>/<version>/ddl/<dialect>/<elements>`
- Drop DDL at `/<model>/<version>/drop/<dialect>/`
- Drop DDL for only `table`, `constraint`, or `index` elements at `/<model>/<version>/drop/<dialect>/<elements>`
- Data deletion DML at `/<model>/<version>/delete/<dialect>/`
- ERDs at `/<model>/<version>/erd/`
- Oracle logging scripts at `/<model>/<version>/logging/oracle/`
- Oracle logging scripts for only `table` or `index` elements at `/<model>/<version>/logging/oracle/<elements>/`
- Oracle nologging scripts at `/<model>/<version>/nologging/oracle/`
- Oracle nologging scripts for only `table` or `index` elements at `/<model>/<version>/logging/oracle/<elements>/`

### With Docker:

Usage:

```sh
docker run dbhi/data-models-sqlalchemy gunicorn -h
```

Run:

```sh
docker run dbhi/data-models-sqlalchemy  # Uses Dockerfile defaults of 0.0.0.0:80
```

### Without Docker:

Install Flask:

```sh
pip install Flask
```

Usage Message:

```sh
dmsa -h
```

Run:

```sh
dmsa serve                              # Uses Flask defaults of 127.0.0.1:5000
```

### Caching data from the data models service

`dmsa` caches model names and versions from the data models service to avoid unnecessary heavy-weight requests. When data models are updated, this cache needs to be refreshed. There are two mechanisms to ensure that a refresh occurs. First, a Github push webhook can be created on the data-models repository used by the data models service. When `dmsa` receives the webhook request to `/refresh`, it refreshes the cache after waiting for 10 seconds to give the data models service a chance to absorb the changes itself. The webhook secret key, if any, can be passed to `dmsa` via the `DMSA_WEBHOOK_SECRET` environment variable.

The second refresh mechanism is a periodic refresh occurring once an hour as a backstop in case the webhook doesn't work or the data models service fails to refresh itself quickly enough.

Both mechanisms use `threading.Timer`, and each process will have 1 or 2 timer threads running (2 after a webhook). Because of this, using `Ctrl-C` (`INT` signal) doesn't work to quit the process in a timely fashion if running on the command line during development. You can stop the process immediately with `kill -TERM <pid>`.

When running under `gunicorn` (as in the Docker container), the master process will kill the workers after 30 seconds when sent an `INT`, `QUIT`, or `TERM` signal.

When running under Docker and the container is stopped, the `gunicorn` processes will all be killed with `SIGKILL` after 10 seconds (or whatever the grace period has been configured as). Ordinarily this is not a great idea, but only the timer threads will be abruptly terminated.

#### Caching notes

The caching is very partial; it could be extended to all requests from the data models service, but it's probably not worth it.

The caching is also not very intelligent in that there is no coordination between the periodic threads and the webhook thread or between the gunicorn processes in order to minimize the number of requests. It would be possible, for instance, to keep track of the data-models repo commit hash being used by the data models service and only refresh the data if that hash has changed.

## Deployment

Deployment of the DBHi `data-models-sqlalchemy.research.chop.edu` service is managed via the internal devops/data-models-sqlalchemy repo.
