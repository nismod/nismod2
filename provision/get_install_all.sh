#
# Get data and install all models
# - utility script duplicating part of vm_provision.sh, run all or part to get or update data
#   and/or models
#


# Get scenarios
bash -x ./provision/get_data_scenarios.sh .

# Digital comms
bash -x ./provision/get_data_digital_comms.sh .
bash -x ./provision/install_digital_comms.sh .

# Energy demand
bash -x ./provision/get_data_energy_demand.sh .
bash -x ./provision/install_energy_demand.sh .
energy_demand setup -f ./models/energy_demand/wrapperconfig.ini

# Energy supply
bash -x ./provision/get_data_energy_supply.sh .
# use default dbconfig if no other provided
cp --no-clobber ./provision/template.dbconfig.ini ./provision/dbconfig.ini
# run install as vagrant to set up ODBC connection
bash -x ./provision/install_energy_supply.sh .

# Transport
bash -x ./provision/get_data_transport.sh .
bash -x ./provision/install_transport.sh .

# ET-Module
bash -x ./provision/get_data_et_module.sh .
bash -x ./provision/install_et_module.sh .

# Water supply
bash -x ./provision/get_data_water_supply.sh .
bash -x ./provision/install_water_supply.sh .

# Water demand
bash -x ./provision/get_data_water_demand.sh .
bash -x ./provision/install_water_demand.sh .
