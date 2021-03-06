#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[digital-comms\]" $base_path/provision/config.ini | tail -n3)"

# Install digital_comms
pip install git+https://github.com/nismod/digital_comms.git@$model_version#egg=digital_comms --upgrade

# Setup wrapper config
cat > $base_path/models/digital_comms/wrapperconfig.ini << EOF
[PATHS]
path_local_data = $base_path/data/digital_comms/processed
EOF
