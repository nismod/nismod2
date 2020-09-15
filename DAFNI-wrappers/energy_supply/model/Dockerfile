FROM docker.pkg.github.com/rosedickinson/nismod2/energy_supply-model_base:latest

WORKDIR /code/nismod2
COPY dockerFiles/dbconfig.ini ./provision/dbconfig.ini
COPY dockerFiles/odbc_config.ini ./install/odbc_config.ini
COPY dockerFiles/database_stuff.sh /code/nismod2/database_stuff.sh
RUN chmod 777 /code/nismod2/database_stuff.sh \
&&  mkdir -p /code/xpress
COPY dockerFiles/*.py /code/nismod2/
COPY dockerFiles/energy_supply_v2.8 /code/nismod2/install/energy_supply
COPY dockerFiles/energy_supply_v2.8/*.bim /code/xpress/dso/

CMD python3 job_processing_wrapper.py