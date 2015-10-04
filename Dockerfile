FROM python:2.7

MAINTAINER Aaron Browne <brownea@email.chop.edu>

# Install Oracle client C header files.
COPY lib/ /app/lib/
RUN apt-get -qq update && apt-get -qq install -y unzip
RUN unzip -qq /app/lib/instantclient-basic-linux.x64-11.2.0.4.0.zip \
    -d /usr/local/lib
RUN unzip -qq /app/lib/instantclient-sdk-linux.x64-11.2.0.4.0.zip \
    -d /usr/local/lib
RUN ln -s /usr/local/lib/instantclient_11_2/libclntsh.so.11.1 \
    /usr/local/lib/instantclient_11_2/libclntsh.so

# Set Oracle environment variables
ENV ORACLE_HOME /usr/local/lib/instantclient_11_2
ENV LD_LIBRARY_PATH /usr/local/lib/instantclient_11_2

# Install Oracle (libaio1) and Postgres (libpq-dev)
# and MSSQL (unixodbc-dev) and ERAlchemy (graphviz)
# package dependencies.
RUN apt-get -qq update && \
    apt-get -qq install -y \
    graphviz \
    libaio1 \
    libpq-dev \
    unixodbc-dev && \
    rm -rf /var/lib/apt/lists/*

# Finally install Python dependencies.
COPY requirements.txt /app/
RUN pip install -r /app/requirements.txt && pip install \
    cx-Oracle==5.1.3 \
    psycopg2==2.6 \
    MySQL-python==1.2.5 \
    pyodbc==3.0.10 \
    gunicorn==19.3.0

# Copy app files.
COPY . /app/

# Install app.
RUN pip install /app/

# Set up run environment.
EXPOSE 80
WORKDIR /app
CMD ["gunicorn", "--bind=0.0.0.0:80", "--workers=4", "dmsa.service:app"]
