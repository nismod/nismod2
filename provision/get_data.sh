#!/usr/bin/env bash
model_name=$1
base_path=$2

# Get password from ftp.ini when not set by environment variable (Gitlab-CI pipeline)
if [ -z "$ftp_username" ] && [ -z "$ftp_password" ]; then
    echo "ftp credentials not set by environment variable so read from ftp.ini"
    source <(grep = <(grep -A3 '\[ftp-config\]' $base_path/provision/ftp.ini))
fi

# Post install
source <(grep = <(grep -A2 "\[$model_name\]" $base_path/provision/config.ini))
target=$base_path/$target

echo "Downloading ${model_name} from ${ftp_source} and copying to ${target}"

# Prepare directory for data
mkdir -p $target

# Download data from server
export SSHPASS=$ftp_password
sshpass -e sftp -oBatchMode=no -oStrictHostKeyChecking=no -b - $ftp_username@$ftp_server << !
   lcd $target
   get $ftp_source
   bye
!

if [ $? -ne 0 ]; then
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    printf "${RED}Unable to download the ${model_name} data files from the SFTP server.${NC}\n"
    printf "${RED}Make sure that the server is responsive, ftp environment vars are set${NC}\n"
    printf "${RED}or the credentials in provision/ftp.ini are correct.${NC}\n"
    exit 1
fi

# Unpack / overwrite existing files
unzip -o $target/*.zip -d $target
rm $target/*.zip
