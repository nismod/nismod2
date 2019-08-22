#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Set the required model version and install directly from GitHub
model_version=v2.0
pip install git+https://github.com/nismod/water_demand.git@$model_version#egg=water_demand
