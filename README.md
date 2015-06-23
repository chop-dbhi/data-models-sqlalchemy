# Data Models SQLAlchemy

SQLAlchemy models and DDL and ERD generation for chop-dbhi/data-models style JSON endpoints.

## SQLAlchemy Models

In your shell, hopefully within a virtualenv:

```sh
pip install dmsa
```

In python:

```python
from dmsa.omop.v5.models import Base

for tbl in Base.metadata.sorted_tables():
    print tbl.name
```

Or:

```python
from dmsa.pedsnet.v2.models import Person, VisitPayer

print VisitPayer.columns
```

These models are dynamically generated at runtime from JSON endpoints provided by chop-dbhi/data-models-service, which reads data stored in chop-dbhi/data-models. It should be simple to add modules for any additional data models that become available, but the currently provided ones are:

- **OMOP V4** at `omop.v4.models`
- **OMOP V5** at `omop.v5.models`
- **PEDSnet V1** at `pedsnet.v1.models`
- **PEDSnet V2** at `pedsnet.v2.models`
- **i2b2 V1.7** at `i2b2.v1_7.models`
- **i2b2 PEDSnet V2** at `i2b2.pedsnet.v2.models`
- **PCORnet V1** at `pcornet.v1.models`
- **PCORnet V2** at `pcornet.v2.models`
- **PCORnet V3** at `pcornet.v3.models`

## DDL and ERD Generation

Use of the included Dockerfile is highly recommended to avoid installing DBMS and graphing specific system requirements.

The following DBMS dialects are supported when generating DDL:

- **PostgreSQL** called as `postgresql`
- **MySQL** called as `mysql`
- **MS SQL Server** called as `mssql`
- **Oracle** called as `oracle`

### With Docker:

Retrieve the image:

```sh
docker pull dbhi/data-models-sqlalchemy
```

Usage for DDL generation:

```sh
docker run --rm dbhi/data-models-sqlalchemy ddl -h
```

Generate OMOP V5 DDL for Oracle:

```sh
docker run --rm dbhi/data-models-sqlalchemy ddl omop v5 oracle
```

Usage for ERD generation:

```sh
docker run --rm dbhi/data-models-sqlalchemy erd -h
```

Generate i2b2 PEDSnet V2 ERD (the image will land at `./erd/i2b2_pedsnet_v2_erd.png`):

```sh
docker run --rm -v $(pwd)/erd:/erd dbhi/data-models-sqlalchemy erd i2b2_pedsnet v2 /erd/i2b2_pedsnet_v2_erd.png
```

The `graphviz` graphing package supports a number of other output formats, listed here (link pending), which are interpreted from the passed extension.

### Without Docker:

Install the system requirements (see Dockerfile for details):

- **Python 2.7**
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
```

Install the data-models-sqlalchemy python package:

```sh
pip install dmsa
```

Usage for DDL generation:

```sh
dmsa ddl -h
```

Generate OMOP V5 DDL for Oracle:

```sh
dmsa ddl omop v5 oracle
```

Usage for ERD generation:

```sh
dmsa erd -h
```

Generate i2b2 PEDSnet V2 ERD (the image will land at `./erd/i2b2_pedsnet_v2_erd.png`):

```sh
mkdir erd
dmsa erd i2b2_pedsnet v2 ./erd/i2b2_pedsnet_v2_erd.png
```

## Web Service

The web service uses a simple Flask debug server for now. It exposes the following endpoints:

- DDL at `/<model>/<version>/ddl/<dialect>/`
- DDL for only `table`, `constraint`, or `index` elements at `/<model>/<version>/ddl/<dialect>/<elements>`
- ERDs at `/<model>/<version>/erd/`

### With Docker:

Usage:

```sh
docker run  dbhi/data-models-sqlalchemy start -h
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

Usage:

```sh
dmsa start -h
```

Run:

```sh
dmsa start                              # Uses Flask defaults of 127.0.0.1:5000
```
