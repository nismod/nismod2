#!/usr/bin/env bash

# Usage:
#    bash provision/run_energy_supply_migrations.sh . minimal
#    bash provision/run_energy_supply_migrations.sh . full

# Expect NISMOD dir as first argument
base_path=$1
minimal_or_full=$2

# Read dbname, host, user, password, port from dbconfig.ini
source <(grep = <(grep -A5 "\[energy-supply\]" $base_path/provision/dbconfig.ini))

# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[energy-supply\]" $base_path/provision/config.ini))

MODEL_DIR=$base_path/install
DATA_DIR=$base_path/$local_dir
MIGRATIONS_DIR=$MODEL_DIR/energy_supply/migrations

# Run migrations
PGPASSWORD=$password \
PGHOST=$host \
PGUSER=$user \
PGPORT=$port \
PGDATABASE=$dbname \
    python $MODEL_DIR/energy_supply/run_migrations.py \
    -r $DATA_DIR/database_$minimal_or_full $MIGRATIONS_DIR