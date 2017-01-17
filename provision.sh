# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python3-pip python3
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


# Provision script for the transport model
bash /vagrant/provision/transport.sh

# Provision script for the solid waste model

# Create roles for solid waste database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'runcdamrole';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE runcdamrole;\" "

su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'sosadministratorrole';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE sosadministratorrole;\" "

su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'djrole';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE djrole;\" "

su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'scr1';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE scr1;\" "


# Upgrade - with non-interactive flags so grub/sudo don't hang on config changes
DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" \
    -o Dpkg::Options::="--force-confold" -yq upgrade

# Add package repository for dotnet core
echo "deb [arch=amd64] https://apt-mo.trafficmanager.net/repos/dotnet-release/ xenial main" > /etc/apt/sources.list.d/dotnetdev.list
apt-key adv --keyserver apt-mo.trafficmanager.net --recv-keys 417A0893
apt-get update
# Install dotnet core (version latest as of 2016-11-28)
apt-get install -y dotnet-dev-1.0.0-preview2.1-003177 --allow-unauthenticated

# Restore dependencies for the solid waste model
cd /vagrant/models/solid_waste/src/SolidWasteModel
dotnet restore
cd /vagrant/models/solid_waste/test/SolidWasteModel.Tests
dotnet restore
