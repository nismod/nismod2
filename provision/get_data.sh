#!/usr/bin/env bash

# Post install
source <(grep = <(grep -A3 '\[ftp-config\]' /vagrant/provision/ftp.ini))
source <(grep = <(grep -A2 "\[$1\]" /vagrant/provision/config.ini))

echo "Downloading ${1} from ${ftp_source} and copying to ${target}"

# Prepare directory for data
mkdir -p $target

# Download data from server
export SSHPASS=$password
sshpass -e sftp -oBatchMode=no -oStrictHostKeyChecking=no -b - $username@$ftp_server << !
   lcd $target
   get $ftp_source
   bye
!

if [ $? -ne 0 ]; then
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    printf "${RED}Unable to download the ${1} datafiles from the SFTP server.${NC}\n"
    printf "${RED}Make sure that the server is responsive and the credentionals in provision/ftp.ini are correct.${NC}\n"
    exit 1
fi

# Unpack / overwrite existing files
unzip -o $target/*.zip -d $target
rm $target/*.zip