FROM docker.pkg.github.com/rosedickinson/nismod2/energy_supply-model_base:latest

WORKDIR /code/nismod2
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/dbconfig.ini ./provision/dbconfig.ini
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/odbc_config.ini ./install/odbc_config.ini
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/database_stuff.sh /code/nismod2/database_stuff.sh
RUN chmod 777 /code/nismod2/database_stuff.sh
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/*.py /code/nismod2/
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/energy_supply_v2.8 /code/nismod2/install/energy_supply
COPY ./DAFNI-wrappers/energy_supply/model/dockerFiles/energy_supply_v2.8/*.bim /code/xpress/dso/
