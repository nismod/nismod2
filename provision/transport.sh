#!/usr/bin/env bash

# install packages
apt-get install -y default-jre

# Get the data from the ftp
. /vagrant/provision/get_data.sh transport

# Download the model jar
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/config.ini))
source <(grep = <(grep -A3 "\[transport\]" /vagrant/provision/config.ini))

MODEL_DIR=/vagrant/install
DATA_DIR=$target
FILENAME=transport_$release.zip
TMP=/vagrant/tmp

mkdir -p $MODEL_DIR
mkdir -p $TMP

export SSHPASS=$password
sshpass -e sftp -oBatchMode=no -oStrictHostKeyChecking=no -b - $username@$ftp_server << !
   lcd $TMP
   get /releases/transport/$FILENAME
   bye
!

unzip $TMP/$FILENAME -d $MODEL_DIR
mv $MODEL_DIR/transport_$release $MODEL_DIR/transport
