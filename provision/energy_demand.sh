#!/usr/bin/env bash

# Install tkinter as requirement for matplotlib
apt-get install -y python3-tk

# pip3 install -e /vagrant/models/energy_demand
VERSION=6cc5ebd
pip3 install git+https://github.com/nismod/energy_demand.git@$VERSION#egg=energy_demand

# Post install
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/config.ini))
source <(grep = <(grep -A2 '\[energy-demand\]' /vagrant/provision/config.ini))

# Prepare directory for data
mkdir -p "$target"

# # Download data from server
# export SSHPASS=$password
# sshpass -e sftp -oBatchMode=no -oStrictHostKeyChecking=no -b - $username@$ftp_server << !
#    lcd $target
#    get $source
#    bye
# !

# if [ $? -ne 0 ]; then
#     RED='\033[0;31m'
#     NC='\033[0m' # No Color
#     printf "${RED}Unable to download the energy_demand datafiles from the Smif FTP server.${NC}\n"
#     printf "${RED}Make sure that the server is responsive and the config.ini information is correct.${NC}\n"
#     exit 1
# fi

# Unpack / overwrite existing files
unzip -o $target\*.zip -d $target
rm $target*.zip

# Post install
energy_demand minimal_setup -d /vagrant/data_energy_demand

# Overwrite the wrapper config to local paths
rm /vagrant/models/energy_demand/wrapperconfig.ini
echo "[PATHS]" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_local_data = /vagrant/models/energy_demand/" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_processed_data = /vagrant/models/energy_demand/_processed_data" >> /vagrant/models/energy_demand/wrapperconfig.ini
echo "path_result_data = /vagrant/models/energy_demand/_result_data" >> /vagrant/models/energy_demand/wrapperconfig.ini