#!/usr/bin/env bash

base_path=$1

source <(grep = <(grep -A3 "\[digital-comms\]" $base_path/provision/config.ini))
pip3 install git+https://github.com/nismod/digital_comms.git@$release#egg=digital_comms

# Setup wrapper
cat > $base_path/models/digital_comms/wrapperconfig.ini << EOF
[PATHS]
path_local_data = $base_path/data/digital_comms/processed
EOF
