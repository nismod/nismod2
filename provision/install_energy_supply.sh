#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1
XPRESS_DIR=$2

#
# Set up ODBC database connection
#

# Read dbname, host, user, password, port from dbconfig.ini
source <(grep = <(grep -A5 "\[energy-supply\]" $base_path/provision/dbconfig.ini))

# Create connection template file
odbc_config_path=$base_path/install/odbc_config.ini
cat > $odbc_config_path << EOF
[energy_supply]
Description=Energy Supply Data
Driver=PostgreSQL Unicode
Trace=Yes
TraceFile=sql.log
Database=$dbname
Servername=$host
UserName=$user
Password=$password
Port=$port
Protocol=6.4
ReadOnly=No
RowVersioning=No
ShowSystemTables=No
ShowOidColumn=No
FakeOidIndex=No
ConnSettings=
EOF

# Install ODBC connection
odbcinst -i -s -f $odbc_config_path

#
# Download and install the energy_supply model
#

# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[energy-supply\]" $base_path/provision/config.ini))

MODEL_DIR=$base_path/install
DATA_DIR=$base_path/$local_dir
FILENAME=energy_supply_$model_version.zip
MIGRATIONS_DIR=$MODEL_DIR/energy_supply/migrations
TMP=$base_path/tmp

mkdir -p $MODEL_DIR
mkdir -p $TMP

python $base_path/provision/get_data.py /releases/energy_supply/$FILENAME $TMP

rm -rf $MODEL_DIR/energy_supply
rm -rf $MODEL_DIR/energy_supply_$model_version
unzip $TMP/$FILENAME -d $MODEL_DIR && mv -f $MODEL_DIR/energy_supply_$model_version $MODEL_DIR/energy_supply

# This is a bit of a hack which places the compiled BIM files into the XPRESS package directory
cp $MODEL_DIR/energy_supply/*.bim $XPRESS_DIR/dso

# Run migrations
PGPASSWORD=$password \
PGHOST=$host \
PGUSER=$user \
PGPORT=$port \
PGDATABASE=$dbname \
    python $MODEL_DIR/energy_supply/run_migrations.py \
    -r $DATA_DIR/database_minimal $MIGRATIONS_DIR
