# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python3 python3-pip python3-dev \
    postgresql postgresql-contrib libpq-dev gdal-bin libspatialindex-dev \
    libgeos-dev python-glpk glpk-utils

# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"
# Database config to listen on network connection
sed -i "s/#\?listen_address.*/listen_addresses '*'/" /etc/postgresql/9.5/main/postgresql.conf
# Allow password connections from any IP (so includes host)
echo "host    all             all             all                     md5" >> /etc/postgresql/9.5/main/pg_hba.conf
# Restart postgres to pick up config changes
service postgresql restart

# use ubuntu package to install latest pip
pip3 install --upgrade pip

# Install smif
pip3 install smif~=0.2 --upgrade

# Install pyscopg2 (required by some run.py wrappers)
pip3 install psycopg2 pytest

# copy bash config to vagrant home
cat /vagrant/config/.bashrc | tr -d '\r' > /home/vagrant/.bashrc
chown vagrant:vagrant /home/vagrant/.bashrc

# Provision digital_comms model
tr -d '\r' < /vagrant/provision/digital_comms.sh > /tmp/digital_comms.sh
bash /tmp/digital_comms.sh

# Provision energy_demand model
tr -d '\r' < /vagrant/provision/energy_demand.sh > /tmp/energy_demand.sh
bash /tmp/energy_demand.sh

# Provision energy_supply model
tr -d '\r' < /vagrant/provision/energy_supply.sh > /tmp/energy_supply.sh
bash /tmp/energy_supply.sh

# Provision solid_waste model
tr -d '\r' < /vagrant/provision/solid_waste.sh > /tmp/solid_waste.sh
bash /tmp/solid_waste.sh

# Provision transport model
tr -d '\r' < /vagrant/provision/transport.sh > /tmp/transport.sh
bash /tmp/transport.sh
