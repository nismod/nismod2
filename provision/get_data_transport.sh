#!/usr/bin/env bash

# Get the data from the ftp
base_path=$1
. $base_path/provision/get_data.sh transport $base_path
