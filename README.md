# NISMOD v2.0

NISMOD v2 will import the integration framework and each of the sector models
to be developed as part of the MISTRAL project, building on work done for
ITRC/NISMOD v1.

## Vagrant notes

The Vagrantfile defines the automated setup for a virtual machine, which will
provide a reproducible development environment.

To use it, first install:

1. [Virtualbox](www.virtualbox.org)
1. [Vagrant](vagrantup.com)


Note for Ubuntu 17.10 users: If you are experiencing the issue *The box ‘bento/ubuntu-16.04’ could not be found or could not be accessed in the remote catalog.* Make sure that you have the latest version of Vagrant (>v2) installed. This version is currently not in the standard package archive (PPA) but can be downloaded from the vagrant website.

### Running for the first time

Then on the command line, from this directory, run:

    git checkout v2 # Checks out the NISMOD v2.0 branch
    git submodule init
    git submodule update
    vagrant up

This will download a virtual machine image and install all the packages and
software which are required to test and run NISMOD onto that virtual machine.

Once that has finished, restart the machine.

    vagrant reload

Now, enter the virtual machine, navigate to the project folder
and run the tests:

    vagrant ssh
    cd /vagrant/test
    pytest

Within `test/model_configurations` there are a set of sample model
configurations.

### Updating your NISMOD v2.0

If a new version of NISMOD v2.0 is released, follow these instructions:

    git checkout v2
    git pull # Pull down the latest changes
    git submodule update # Update the sector models
    vagrant reload --provision # Restart and re-provision the virtual machine


### Integration testing

The tests in this repository are intended to test the integration of the various
NISMOD sector models with `smif`, the simulation modelling integration
framework. In outline, tests here should:

- validate possible system-of-systems model configurations
- run each sector model through `smif` with only scenario dependencies (not
  coupling with any other models)
    1. without unexpected error
    1. with the expected type contract of results
- run combinations of sector models
    1. without unexpected error
    1. with the expected type contract of results
    1. (optionally) with regression tests against known-good modelled outputs
