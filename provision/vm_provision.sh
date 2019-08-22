#!/usr/bin/env bash

#
# Provision virtual machine
#
# This script is expected to run a part of the vagrant virtual machine provisioning process. It
# is run by the root user and should do all required installation and setup:
#   1. Install OS packages
#   2. Install any other programs required by models (e.g. custom install/setup)
#   3. Provision services required by models (including smif and Postgres databases)
#   4. Download data required for model setup
#   5. Install models
#   6. Light-touch set up of virtual machine environment for user convenience (other programs
#      or dependencies, .bashrc or other dotfiles)
#

# Expect base path as the only argument (default to current working directory)
if [ -z "$1" ]; then
    base_path=.
else
    base_path=$1
fi

# Echo commands as they are executed
set -x

# Create vagrant user if not exists
id -u vagrant >/dev/null 2>&1 || useradd --create-home vagrant


#
# Install OS packages
#

apt-get update
# Install:
# - basics:  build-essential git vim-nox
# - python with pip and venv, tk for matplotlib:  python3 python3-pip python3-dev python3-tk python3-venv
# - postgres:  postgresql postgresql-contrib libpq-dev odbc-postgresql unixodbc-dev
# - spatial shared libs:  gdal-bin libspatialindex-dev libgeos-dev
# - Java for transport: default-jre
apt-get install -y \
    build-essential git vim-nox wget curl \
    python3 python3-pip python3-dev python3-tk python3-venv \
    postgresql postgresql-contrib libpq-dev odbc-postgresql unixodbc-dev \
    gdal-bin libspatialindex-dev libgeos-dev \
    default-jre


#
# Install FICO XPRESS for energy supply
#

XPRESS_VERSION="8.5.10"
XPRESS_URL="https://clientarea.xpress.fico.com/downloads/${XPRESS_VERSION}/xp${XPRESS_VERSION}_linux_x86_64_setup.tar"
XPRESS_PKG="xp${XPRESS_VERSION}_linux_x86_64.tar.gz"
XPRESS_DIR=/home/vagrant/xpress
XPRESS_LICENSE=$XPRESS_DIR/bin/xpauth.xpr
XPRESS_BIN=$XPRESS_DIR/bin
TMP=$base_path/tmp

if [[ -e "$TMP/$XPRESS_PKG" ]]; then
    echo "Got $TMP/$XPRESS_PKG"
else
    # Download FICO XPRESS
    wget -nc -qO- $XPRESS_URL --no-check-certificate | tar -C $TMP -xv
fi

# Unpack FICO XPRESS
mkdir -p $XPRESS_DIR
mkdir -p $XPRESSDIR/lib/backup
mv $XPRESSDIR/lib/lib* $XPRESSDIR/lib/backup 2>/dev/null # Avoid unpacking errors
tar -C $XPRESS_DIR -xf $TMP/$XPRESS_PKG

# Copy FICO XPRESS license
# use default if no other provided
cp --no-clobber $base_path/provision/template.xpauth.xpr $base_path/provision/xpauth.xpr
cp $base_path/provision/xpauth.xpr $XPRESS_DIR/bin/xpauth.xpr

# Setup FICO XPRESS environment variables
cat > $XPRESS_DIR/bin/xpvars.sh << EOF
XPRESS_DIR=$XPRESS_DIR
XPRESS=$XPRESS_BIN
LD_LIBRARY_PATH=\${XPRESS_DIR}/lib:\${LD_LIBRARY_PATH}
DYLD_LIBRARY_PATH=\${XPRESS_DIR}/lib:\${DYLD_LIBRARY_PATH}
SHLIB_PATH=\${XPRESS_DIR}/lib:\${SHLIB_PATH}
LIBPATH=\${XPRESS_DIR}/lib:\${LIBPATH}
PYTHONPATH=\${XPRESS_DIR}/lib:\${PYTHONPATH}

CLASSPATH=\${XPRESS_DIR}/lib/xprs.jar:\${CLASSPATH}
CLASSPATH=\${XPRESS_DIR}/lib/xprb.jar:\${CLASSPATH}
CLASSPATH=\${XPRESS_DIR}/lib/xprm.jar:\${CLASSPATH}
PATH=\${XPRESS_DIR}/bin:\${PATH}

if [ -f "${XPRESS_DIR}/bin/xpvars.local.sh" ]; then
  . ${XPRESS_DIR}/bin/xpvars.local.sh
fi

export LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH
export SHLIB_PATH
export LIBPATH
export PYTHONPATH
export CLASSPATH
export XPRESS_DIR
export XPRESS
EOF


#
# Setup PostgreSQL database(s) (used by energy supply)
#

# Ensure postgres is running
service postgresql start
# Ensure en_US locale exists
locale-gen en_US.UTF-8
# Database config to listen on network connection
sed -i "s/#\?listen_address.*/listen_addresses '*'/" /etc/postgresql/9.5/main/postgresql.conf
# Allow password connections from any IP (so includes host)
echo "host    all             all             all                     md5" >> /etc/postgresql/9.5/main/pg_hba.conf
# Restart postgres to pick up config changes
service postgresql restart

# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"


#
# Install python packages
#

# set up env
pyvenv nismod
source nismod/bin/activate

# Install smif
pip install --upgrade pip
pip install --upgrade setuptools wheel
pip install pyscaffold
pip install smif~=1.2 --upgrade
pip install smif[data]~=1.2
pip install smif[spatial]~=1.2

# Install Jupyter Notebook for Results Viewer
pip install jupyter notebook
pip install networkx matplotlib numpy ipywidgets

# Install pyscopg2 (required by some run.py wrappers)
pip install psycopg2-binary pytest

# Install aws cli and boto3 library to access Amazon S3
pip install --upgrade awscli
pip install --upgrade boto3

# Further requirements for provision python scripts
pip install requests pandas


#
# Download data and install models
#

# We MUST clean ALL the windows newlines, otherwise the scripts below fail noisily
shopt -s nullglob
to_clean=($base_path/provision/*)
shopt -u nullglob

for filename in ${to_clean[@]}; do
    bname=$(basename $filename)
    tr -d '\r' < $filename > /tmp/$bname
    mv /tmp/$bname $filename
done;

# Add to known hosts
declare -a hosts=("github.com" "sage-itrc.ncl.ac.uk" "128.240.212.101")
# Ensure own .ssh
mkdir -p ~/.ssh
chmod 700 ~/.ssh
# Ensure vagrant .ssh
mkdir -p /home/vagrant/.ssh
chown -R vagrant:vagrant /home/vagrant/.ssh
chmod 700 /home/vagrant/.ssh
for host in "${hosts[@]}"
do
    ssh-keyscan $host >> ~/.ssh/known_hosts
    su vagrant -c "ssh-keyscan $host >> /home/vagrant/.ssh/known_hosts"
done

# Get scenarios
bash -x $base_path/provision/get_data_scenarios.sh $base_path

# Digital comms
bash -x $base_path/provision/get_data_digital_comms.sh $base_path
bash -x $base_path/provision/install_digital_comms.sh $base_path

# Energy demand
bash -x $base_path/provision/get_data_energy_demand.sh $base_path
bash -x $base_path/provision/install_energy_demand.sh $base_path
energy_demand setup -f $base_path/models/energy_demand/wrapperconfig.ini

# Energy supply
bash -x $base_path/provision/get_data_energy_supply.sh $base_path
# use default dbconfig if no other provided
cp --no-clobber $base_path/provision/template.dbconfig.ini $base_path/provision/dbconfig.ini
# run install as vagrant to set up ODBC connection
su vagrant -c "bash -x $base_path/provision/install_energy_supply.sh $base_path $XPRESS_DIR"

# Transport
bash -x $base_path/provision/get_data_transport.sh $base_path
bash -x $base_path/provision/install_transport.sh $base_path

# ET-Module
bash -x $base_path/provision/get_data_et_module.sh $base_path
bash -x $base_path/provision/install_et_module.sh $base_path

# Water supply
bash -x $base_path/provision/get_data_water_supply.sh $base_path
bash -x $base_path/provision/install_water_supply.sh $base_path

# Water demand
bash -x $base_path/provision/get_data_water_demand.sh $base_path
bash -x $base_path/provision/install_water_demand.sh $base_path


#
# User config
#

# Make virtualenv user-editable
chown -R vagrant:vagrant /home/vagrant/nismod

# Copy bash config to vagrant home
if [ "$base_path" == "/vagrant" ]; then
    tr -d '\r' < $base_path/provision/.bashrc > /home/vagrant/.bashrc
    chown vagrant:vagrant /home/vagrant/.bashrc
fi
