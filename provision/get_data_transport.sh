#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Download full (Great Britain) data
# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A4 "\[transport\]" $base_path/provision/config.ini))
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir
mv $base_path/$local_dir/TR_data_full_* $base_path/$local_dir/TR_data_full
rm -r $base_path/$local_dir/gb
mkdir -p $base_path/$local_dir/gb/config
mv $base_path/$local_dir/TR_data_full/full/data $base_path/$local_dir/gb/data


# Download test (Southampton) data
source <(grep = <(grep -A3 "\[transport-test\]" $base_path/provision/config.ini))
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir
mv $base_path/$local_dir/transport_testdata* $base_path/$local_dir/transport_testdata
rm -r $base_path/$local_dir/southampton
mkdir -p $base_path/data/transport/southampton/config
mv $base_path/$local_dir/transport_testdata $base_path/$local_dir/southampton/data

# gzip routes as expected by model
gzip $base_path/$local_dir/southampton/data/routes/passengerRoutes.dat
gzip $base_path/$local_dir/southampton/data/routes/freightRoutes.dat
