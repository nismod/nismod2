#!/usr/bin/env bash

# install packages
apt-get install -y default-jdk maven

# compile and package project
su vagrant <<'EOF'
cd /vagrant/models/transport/transport/
mvn clean install
EOF
