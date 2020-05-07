#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Download full (Great Britain) data
# Read model_version, remote_data, local_dir from config.ini
eval "$(grep -A3 "\[transport\]" $base_path/provision/config.ini | tail -n3)"
rm -rf $base_path/$local_dir/TR_data_full
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir
filename=$(basename $remote_data)
dirname="${filename%.*}"
mv $base_path/$local_dir/$dirname $base_path/$local_dir/TR_data_full
rm -rf $base_path/$local_dir/gb
mkdir -p $base_path/$local_dir/gb/config
mv $base_path/$local_dir/TR_data_full/full/data $base_path/$local_dir/gb/data


# Download test (Southampton) data
eval "$(grep -A3 "\[transport-test\]" $base_path/provision/config.ini | tail -n3)"
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir
filename=$(basename $remote_data)
dirname="${filename%.*}"
mv $base_path/$local_dir/$dirname $base_path/$local_dir/transport_testdata
rm -rf $base_path/$local_dir/southampton
mkdir -p $base_path/data/transport/southampton/config
mv $base_path/$local_dir/transport_testdata $base_path/$local_dir/southampton/data

# gzip routes as expected by model
gzip $base_path/$local_dir/southampton/data/routes/passengerRoutes.dat
gzip $base_path/$local_dir/southampton/data/routes/freightRoutes.dat


# Run conversion to smif scenarios

# Baseline
python $base_path/utilities/transport/convert_transport_engine_fractions.py \
    $base_path/$local_dir/gb/data/csvfiles/engineTypeFractions.csv \
    $base_path/data/scenarios/engine_type_fractions.csv

# EW - electric world
python $base_path/utilities/transport/convert_transport_engine_fractions.py \
    $base_path/$local_dir/gb/data/csvfiles/engineTypeFractionsEW.csv \
    $base_path/data/scenarios/engine_type_fractions_ew.csv

# MVE - multi-vector
python $base_path/utilities/transport/convert_transport_engine_fractions.py \
    $base_path/$local_dir/gb/data/csvfiles/engineTypeFractionsMVE.csv \
    $base_path/data/scenarios/engine_type_fractions_mve.csv


# Download rail data
eval "$(grep -A3 "\[transport-rail\]" $base_path/provision/config.ini | tail -n3)"
python $base_path/provision/get_data.py $remote_data $base_path/$local_dir

mv $base_path/$local_dir/transport-rail_$data_version/dimensions/*.csv $base_path/data/dimensions/
mv $base_path/$local_dir/transport-rail_$data_version/initial_conditions/*.csv $base_path/data/initial_conditions/
mv $base_path/$local_dir/transport-rail_$data_version/interventions/*.csv $base_path/data/interventions/
mv $base_path/$local_dir/transport-rail_$data_version/parameters/*.csv $base_path/data/parameters/
mv $base_path/$local_dir/transport-rail_$data_version/scenarios/*.csv $base_path/data/scenarios/
