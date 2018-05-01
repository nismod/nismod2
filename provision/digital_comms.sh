#!/usr/bin/env bash

source <(grep = <(grep -A3 "\[digital-comms\]" /vagrant/provision/config.ini))
pip3 install git+https://github.com/nismod/digital_comms.git@$release#egg=digital_comms

# Post install
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/ftp.ini))

# Prepare directory for data
mkdir -p "$target"

. /vagrant/provision/get_data.sh digital-comms
