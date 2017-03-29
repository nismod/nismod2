# Create roles for solid waste database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'runcdamrole';\" " | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE runcdamrole;\" "
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'sosadministratorrole';\" " | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE sosadministratorrole;\" "
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'djrole';\" " | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE djrole;\" "
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'scr1';\" " | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE scr1;\" "

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
