FROM postgres:11.9

ENV POSTGRES_DB postgres
ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD postgres

RUN apt-get update
RUN apt-get install -y \
  build-essential \
  locate \
  vim-nox \
  python3-pip \
  python3 \
  postgresql-contrib \
  odbc-postgresql \
  unixodbc-dev

EXPOSE 5432
RUN mkdir /code/
COPY ./DAFNI-wrappers/energy_supply/db/setup_db.sh /code/setup_db.sh
RUN chmod 777 /code/setup_db.sh
RUN chmod 0700 /var/lib/postgresql/data
USER postgres

WORKDIR /code

