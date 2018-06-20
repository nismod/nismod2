# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python3 python3-pip python3-dev \
    postgresql postgresql-contrib libpq-dev gdal-bin libspatialindex-dev \
    libgeos-dev python-glpk glpk-utils sshpass

ssh-keyscan -H github.com >> ~/.ssh/known_hosts

# Configure /vagrant folder as default on vagrant ssh
echo "cd /vagrant" >> /home/vagrant/.bashrc

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
hash -r pip # workaround pipv10 breaks Debian/Ubuntu pip3 command

# Install smif
pip3 install -U setuptools
pip3 install pyscaffold
pip3 install smif~=0.7 --upgrade

# Install Jupyter Notebook for Results Viewer
pip3 install jupyter notebook
pip3 install networkx matplotlib numpy ipywidgets

# Install pyscopg2 (required by some run.py wrappers)
pip3 install psycopg2-binary pytest

# We MUST clean ALL the windows newlines
shopt -s nullglob
to_clean=(/vagrant/provision/*)
shopt -u nullglob

for filename in ${to_clean[@]}; do
    bname=$(basename $filename)
    tr -d '\r' < $filename > /tmp/$bname
    mv /tmp/$bname $filename
    echo $bname
done;

# copy bash config to vagrant home
cp /vagrant/provision/.bashrc /home/vagrant/.bashrc
chown vagrant:vagrant /home/vagrant/.bashrc

# # Provision digital_comms model
bash /vagrant/provision/digital_comms.sh

# Provision energy_demand model
bash /vagrant/provision/energy_demand.sh

# Provision energy_supply model
bash /vagrant/provision/energy_supply.sh

# # Provision solid_waste model
# bash /vagrant/provision/solid_waste.sh

# # Provision transport model
bash /vagrant/provision/transport.sh
