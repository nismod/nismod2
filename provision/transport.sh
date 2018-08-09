#!/usr/bin/env bash

base_path=$1

# install packages
apt-get install -y default-jre

# Get the data from the ftp
. $base_path/provision/get_data.sh transport $base_path

# Download the model jar
if [ -z "$ftp_username" ] && [ -z "$ftp_password" ]; then
    source <(grep = <(grep -A3 '\[ftp-config\]' $base_path/provision/ftp.ini))
fi

source <(grep = <(grep -A3 "\[transport\]" $base_path/provision/config.ini))

MODEL_DIR=$base_path/install
DATA_DIR=$target
FILENAME=transport_$release.zip
TMP=$base_path/tmp

mkdir -p $MODEL_DIR
mkdir -p $TMP

export SSHPASS=$ftp_password
sshpass -e sftp -oBatchMode=no -oStrictHostKeyChecking=no -b - $ftp_username@$ftp_server << !
   lcd $TMP
   get /releases/transport/$FILENAME
   bye
!

rm -r $MODEL_DIR/transport
unzip $TMP/$FILENAME -d $MODEL_DIR && mv -f $MODEL_DIR/transport_$release $MODEL_DIR/transport
