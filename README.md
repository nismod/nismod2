# NISMOD v2.0

NISMOD v2 will import the integration framework and each of the sector models
to be developed as part of the MISTRAL project, building on work done for
ITRC/NISMOD v1.

## Running NISMOD in a virtual machine

The Vagrantfile defines the automated setup for a virtual machine, which will
provide a reproducible development environment.

In virtual machine terminology, the virtual machine (vm for short) is sometimes
called the ‘guest’ machine and the physical computer is called the ‘host’
machine.

To use the NISMOD virtual machine, first install:

1. [Virtualbox](https://www.virtualbox.org)
1. [Vagrant](https://vagrantup.com)

If you see only 32-bit options in Virtualbox, please ensure that:
1. Hardware virtualization is enabled in the BIOS
    - For Intel x64: VT-x (Intel Virtualization Technology) and VT-d are both enabled
    - For AMD x64: AMD SVM (Secure Virtual Machine) is enabled
2. For Windows: in Windows Features, "Hyper-V platform" is disabled.

Note for Ubuntu 17.10 users: If you are experiencing the issue *The box
‘bento/ubuntu-16.04’ could not be found or could not be accessed in the remote
catalog.* Make sure that you have the latest version of Vagrant (>v2) installed.
This version is currently not in the standard package archive (PPA) but can be
downloaded from the vagrant website.


### Running for the first time

Then on the command line, from this directory (wherever you have placed the
NISMOD folder, either downloaded as a release or cloned from a git repository),
run:

```bash
git checkout v2      # check out the NISMOD v2 branch
git submodule init
git submodule update
```

Add your credentials for the NISMOD FTP server to `provision/ftp.ini` within the
NISMOD folder:

```
[ftp-config]
ftp_server=ceg-itrc.ncl.ac.uk
username=<username>
password=<password>
```

Create and configure the guest machine:

```bash
vagrant up
```

This will download a virtual machine image and install all the packages and
software which are required to test and run NISMOD onto that virtual machine.

Once it has run, you should be able to:

```bash
vagrant ssh          # log in to the virtual machine on the command line
cd /vagrant          # move to the folder that’s shared between the host and guest machines
ls                   # list files and folders
smif list            # list available model runs
smif run energy_supply_toy  # to run the energy_supply_toy model run
logout               # log out of the virtual machine (or shortcut: CTRL+D)
```

Then results are written to subfolders within the results directory – I’m working with Will on a reasonable way to view intermediate and final results at the moment.


### Database connection

Some sector models use a database which runs within the virtual machine and is
set up when the virtual machine is provisioned.

The virtual machine exposes the database on port 6543 on the host machine, so
you should be able to connect with the following details:

| key      | value     |
|----------|-----------|
| Host     | localhost |
| Database | vagrant   |
| User     | vagrant   |
| Password | vagrant   |
| Port     | 6543      |

For example, on the command line, assuming the `psql` postgres command line
client is installed on the host machine, you should be able to connect with:

    psql -d vagrant -h localhost -U vagrant -p 6543

#### Security note

This database setup is intended for testing and development only and assumes
that high-numbered ports are only accessible to the local user. Strong passwords
and secure login methods should be used if the host machine is expected to be
accessed by multiple users.


### Updating

To update NISMOD to the latest development version:

```bash
cd projects/nismod   # or to wherever you’ve put the nismod folder
git checkout v2      # to make sure you’re on the v2 branch
git pull             # pull changes from Github to your local machine
git submodule update # update the sector models
```

Then reload and re-provision the virtual machine:

```bash
vagrant reload --provision
```


### Integration tests

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
