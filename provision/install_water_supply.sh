#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Read remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[water-supply\]" $base_path/provision/config.ini))

git clone --depth 1 git@github.com:nismod/water_supply.git $local_dir/repo || exit "$?"

cp $local_dir/repo/wathnet/w5_console.exe $local_dir
cp $local_dir/repo/models/National_Model.wat $local_dir

mkdir -p $local_dir/tmp
cp $local_dir/repo/scripts/preprocessing/prepare_nodal.py $local_dir/tmp

rm -rf $local_dir/repo

# Download model data
python $base_path/provision/get_data.py $remote_data $local_dir/tmp

# Prepare the nodal file
python $local_dir/tmp/prepare_nodal.py \
    --FlowFile $local_dir/tmp/National_WRSM_NatModel_logNSE_obs_11018_1.txt \
    --DemandFile $local_dir/tmp/001_daily.csv \
    --CatchmentFile $local_dir/tmp/CatchmentIndex.csv \
    --MissingDataFile $local_dir/tmp/missing_data.csv \
    --OutputFile $local_dir/wathnet.nodal

rm -rf $local_dir/tmp
