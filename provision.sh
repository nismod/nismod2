# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python3-pip python3 postgresql \
    postgresql-contrib

# Database config to listen on network connection
sed -i "s/#listen_address.*/listen_addresses 'localhost'/" \
    /etc/postgresql/9.5/main/postgresql.conf
# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"

# Upgrade - with non-interactive flags so grub/sudo don't hang on config changes
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" -yq upgrade

# use ubuntu package to install latest pip
pip3 install --upgrade pip

# copy bash config to vagrant home
cat /vagrant/config/.bashrc | tr -d '\r' > /home/vagrant/.bashrc
chown vagrant:vagrant /home/vagrant/.bashrc

# Install smif from github repository
pip install git+https://github.com/nismod/smif


# Provision transport model
tr -d '\r' < /vagrant/provision/transport.sh > /tmp/transport.sh
bash /tmp/transport.sh

# Provision solid_waste model
tr -d '\r' < /vagrant/provision/solid_waste.sh > /tmp/solid_waste.sh
bash /tmp/solid_waste.sh

# Provision energy_supply model
tr -d '\r' < /vagrant/provision/energy_supply.sh > /tmp/energy_supply.sh
bash /tmp/energy_supply.sh