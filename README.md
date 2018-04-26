# NISMOD v2.0

NISMOD v2.0 includes the integration framework smif and released versions
for each of the sector models developed as part of the ITRC-MISTRAL project
together with the configuration necessary to get the model communicating as a 
system-of-systems model.

## Vagrant notes

The Vagrantfile defines the automated setup for a virtual machine, which will
provide a reproducible development environment.

To use it, first install:

1. [Virtualbox](www.virtualbox.org)
1. [Vagrant](vagrantup.com)

Note for Ubuntu 17.10 users: If you are experiencing the issue *The box ‘bento/ubuntu-16.04’ could not be found or could not be accessed in the remote catalog.* Make sure that you have the latest version of Vagrant (>v2) installed. This version is currently not in the standard package archive (PPA) but can be downloaded from the vagrant website.

Note for Windows users: Virtualbox requires that Hyper-V is disabled.

## Download NISMOD v2.0

The latest release of NISMOD v2.0 is available from [Github Releases](https://github.com/nismod/nismod/releases/latest).

Download the .zip archive and unzip it into a directory.

Now, goto [Running for the first time](Running for the first time)

## Installing NISMOD v2.0 in Development Mode

Clone the NISMOD v2.0 repository using the command

    git clone http://github.com/nismod/nismod
    
Then on the command line, from this directory, run:

    git checkout v2 # Checks out the NISMOD v2.0 branch
    git submodule init
    git submodule update

Now, goto [Running for the first time](Running for the first time)

## Updating your NISMOD v2.0

If a new version of NISMOD v2.0 is released, follow these instructions:

    git checkout v2
    git pull # Pull down the latest changes
    git submodule update # Update the sector models
    vagrant reload --provision # Restart and re-provision the virtual machine

Now, goto [Running for the first time](Running for the first time)

## Running for the first time

In the install directory, add the credentials for the smif FTP server to `provision/config.ini':

```
[ftp-config]
ftp_server=ceg-itrc.ncl.ac.uk
username=
password=
```

Create and configure the guest machine:

    vagrant up

This will download a virtual machine image, install all the packages and
software which are required to test and run NISMOD onto that virtual machine
and download the data and model releases from the FTP.

Once that has finished successfully, restart the machine.

    vagrant reload

Now, enter the virtual machine, navigate to the project folder
and run smif:

    vagrant ssh
    cd /vagrant
    smif list

All model configuration is contained in the `config` folder, data in the `data`
folder, model wrappers in the `model` folder, and results in the `results` folder

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
