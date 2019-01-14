#!/usr/bin/env bash
base_path=$1

# Prepare directory for data
. $base_path/provision/get_data.sh energy-demand $base_path
. $base_path/provision/get_data.sh energy-demand-config-data $base_path
