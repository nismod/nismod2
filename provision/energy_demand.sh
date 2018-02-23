# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# Install digital_comms from git submodule checkout
pip3 install -e /vagrant/models/energy_demand

# Overwrite the wrapper config to local paths
rm /vagrant/models/energy_demand/wrapperconfig.ini
echo "[PATHS]" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_local_data = /vagrant/models/energy_demand/" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_processed_data = /vagrant/models/energy_demand/_processed_data" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_result_data = /vagrant/models/energy_demand/_result_data" >> /vagrant/models/energy_demand/wrapperconfig.ini
