#!/usr/bin/env bash

#
# Run this script once on first login
#
# To handle mismatched line-endings (e.g. on a Windows host with a Linux guest VM), run:
# tr -d '\r' < post_provision_setup.sh > /tmp/post_provision_setup.sh && bash /tmp/post_provision_setup.sh

# Setup environment variables on login
echo "source /opt/xpressmp/bin/xpvars.sh" >> /home/$(whoami)/.bashrc

# copy bash config to vagrant home
cp ./provision/.bashrc /home/$(whoami)/.bashrc
chown $(whoami):$(whoami) /home/$(whoami)/.bashrc
