FROM continuumio/miniconda3:4.8.2

# Setup environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/opt/conda/envs/nismod/bin:/usr/local/bin/npm:/usr/local/bin:$PATH"

RUN mkdir -p /code/nismod2 /code/datasets/scenarios \
&&  apt-get update \
&&  apt-get install \
    build-essential \
    dirmngr \
    gdal-bin \
    gnupg \
    jq \
    libpq-dev \
    libspatialindex-dev \
    libgeos-dev \
    vim-nox \
    postgresql-11 \
    postgresql-client-11 \
    postgresql-contrib-11 \
    unixodbc-dev \
    odbc-postgresql  \
    software-properties-common -y

COPY ./* /code/nismod2/

# Move python scripts and dbconfig to right place
RUN mv -f /code/nismod2/DAFNI-wrappers/base-image/dockerFiles/* /code/nismod2/ \
&&  mv -f /code/nismod2/requirements.txt /code \
&&  mv -f /code/nismod2/dbconfig.ini /code/nismod2/provision/dbconfig.ini \
&&  chmod 777 ./provision/*

WORKDIR /code
# Installing smif as per NISMOD2 instructions
RUN conda create --name nismod --override-channels -c conda-forge --file /code/requirements.txt python=3.7 -v -v \
# Activate the nismod conda environment
&&  echo "source activate nismod" > ~/.bashrc

WORKDIR /code/nismod2
