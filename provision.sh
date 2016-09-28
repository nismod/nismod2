# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python-pip postgresql \
    postgresql-contrib postgis nginx-core

# Database config to listen on network connection
sed -i "s/#listen_address.*/listen_addresses 'localhost'/" \
    /etc/postgresql/9.5/main/postgresql.conf
# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"
# Add PostGIS extension
su vagrant -c "psql -c \"CREATE EXTENSION IF NOT EXISTS postgis;\" vagrant"

# Upgrade - with non-interactive flags so grub/sudo don't hang on config changes
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" -yq upgrade

pip install --upgrade pip

# Add github to known hosts
mkdir -p ~/.ssh
chmod 700 ~/.ssh
ssh-keyscan -H github.com >> ~/.ssh/known_hosts
ssh -T git@github.com

PYTHON_VERSION=3.5

# Use the miniconda installer for faster download / install of conda
# itself
wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh \
    -O miniconda.sh
chmod +x miniconda.sh && ./miniconda.sh -b -p $HOME/miniconda
PATH=$HOME/miniconda/bin:$PATH
conda update --yes conda

# Configure the conda environment and put it in the path using the
# provided versions
conda create -n testenv --yes python=$PYTHON_VERSION pip
source activate testenv

# Install a version of smif using an editable install
pip install -e git+ssh://git@github.com/nismod/smif.git#egg=smif
