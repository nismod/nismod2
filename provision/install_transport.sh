#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[transport\]" $base_path/provision/config.ini))

# Download model
FILENAME=transport_$model_version.zip
TMP=$base_path/tmp
mkdir -p $TMP
python $base_path/provision/get_data.py releases/transport/$FILENAME $TMP

# Install model jar to local dir
MODEL_DIR=$base_path/install
mkdir -p $MODEL_DIR
rm -rf $MODEL_DIR/transport
unzip $TMP/$FILENAME -d $MODEL_DIR
mv $MODEL_DIR/transport* $MODEL_DIR/transport
