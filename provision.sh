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

# Install a version of smif using an editable install
su vagrant <<'EOF'
cd ~
git clone https://github.com/nismod/smif.git
cd smif/
# Install requirements to vagrant user dir
pip install --user -r requirements.txt
# Use a special install of behave testing framework for now
pip install --user git+https://github.com/behave/behave
pip install --user -r test-requirements.txt
python3 setup.py develop --user
EOF

# Provision script for the transport model
bash /vagrant/models/transport/provision.sh
