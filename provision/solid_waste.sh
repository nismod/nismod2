#!/usr/bin/env bash

# Run db migrations
su vagrant -c "python /vagrant/models/solid_waste/db/run_migrations.py -d"
su vagrant -c "python /vagrant/models/solid_waste/db/run_migrations.py -u"

# Add package repository for dotnet core
echo "deb [arch=amd64] https://apt-mo.trafficmanager.net/repos/dotnet-release/ xenial main" > /etc/apt/sources.list.d/dotnetdev.list
apt-key adv --keyserver apt-mo.trafficmanager.net --recv-keys 417A0893
apt-get update
# Install dotnet core (version latest as of 2017-03-24)
apt-get install -y dotnet-dev-1.0.1

# Restore dependencies for the solid waste model
su vagrant <<'EOF'
cd /vagrant/models/solid_waste/src/SolidWasteModel
dotnet restore
cd /vagrant/models/solid_waste/test/SolidWasteModel.Tests
dotnet restore
EOF
