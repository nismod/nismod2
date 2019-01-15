#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

#
# TODO update and verify this script
#

# # Clone source
# git clone https://github.com/nismod/solid_waste.git $base_path/models/solid_waste

# # Restore dependencies for the solid waste model
# cd $base_path/models/solid_waste/src/SolidWasteModel
# dotnet restore
# cd $base_path/models/solid_waste/test/SolidWasteModel.Tests
# dotnet restore

# # Run db migrations
# python $base_path/models/solid_waste/db/run_migrations.py -d
# python $base_path/models/solid_waste/db/run_migrations.py -u
