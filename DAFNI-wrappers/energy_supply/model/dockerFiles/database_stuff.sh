# bin/bash

base_path=$1

ls -la /data/
echo $PATH
printenv

echo "Installing"
# Install ODBC connection
odbcinst -i -s -f $base_path/install/odbc_config.ini

PGPASSWORD="postgres" \
PGHOST="0.0.0.0" \
PGUSER="postgres" \
PGPORT="5432" \
PGDATABASE="postgres" \
    python3 /code/nismod2/install/energy_supply/run_migrations.py \
    -r /code/nismod2/data/energy_supply/database_full /code/nismod2/install/energy_supply/migrations

echo "Extraction Finished"