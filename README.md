# NISMOD v2.0

NISMOD v2.0 includes the integration framework smif and released versions
for each of the sector models developed as part of the ITRC-MISTRAL project
together with the configuration necessary to get the model communicating as a
system-of-systems model.

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


Note for Windows users: Virtualbox requires that Hyper-V is disabled.

## Download NISMOD v2.0

The latest release of NISMOD v2.0 is available from [Github Releases](https://github.com/nismod/nismod2/releases/latest).

Download the .zip archive and unzip it into a directory.

Now, goto [Running for the first time](Running for the first time)

## Installing NISMOD v2.0 in Development Mode

Clone the NISMOD v2.0 repository using the command

Then on the command line, from this directory (wherever you have placed the
NISMOD folder, either downloaded as a release or cloned from a git repository),
run:

```bash
git checkout master  # check out the NISMOD2 master branch
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

This will download a virtual machine image, install all the packages and
software which are required to test and run NISMOD onto that virtual machine
and download the data and model releases from the FTP.

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

### Viewing Results

The vagrant box hosts a local jupyter notebook server which can be accessed by
nagivating your browser to [`localhost:8910`](http://localhost:8910/notebooks/Results%20Viewer%20-%20Split%20Out.ipynb)

First, spin up the notebook server in the background with the command:

    vagrant ssh
    cd /vagrant
    jupyter notebook &> /dev/null &

### Database Connection

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
git checkout master  # to make sure you’re on the master branch
git pull             # pull changes from Github to your local machine
```

Then reload and re-provision the virtual machine:

```bash
vagrant reload --provision
```

All model configuration is contained in the `config` folder, data in the `data`
folder, model wrappers in the `model` folder, and results in the `results` folder

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

## Development

### General Guidelines

- v2 branch is protected against push and force-push.
- The v2 branch should be treated as live and is used for major releases only
- All development occurs on the `develop` branch
- New features are never added to an existing release branch

For further detail, see this [article](http://nvie.com/posts/a-successful-git-branching-model/)

### Developing a new feature

1. Create a new feature branch from the develop branch `git checkout -b feature/<feature_name> develop`
1. Develop your feature
1. Submit a pull request against the develop branch
1. Merge the changes into the develop branch

### Release Process

1. Update the changelog under the heading Version X.Y
1. Check versions of models and data specified in `provision/config.ini`

1. Now, create a branch from develop e.g. `checkout -b release-x.y develop`
1. Tag this as a release candidate `git tag -a vx.y-rc1`
1. Any bugfixes are committed to this branch and should be tagged with incremented 
   release candidate tags e.g. `git tag -a vx.y-rc2`
1. Once the release candidate is stable, submit a pull request to the `v2` branch
1. Merge the pull request and tag `git tag -a vx.y.0`

### Fixing a Bug in a release

1. Create a branch from master `git checkout -b hotfix/<bug_name> master`
1. Fix the bug by committing to the branch
1. Submit a pull request to master and tag the fix `git tag -a vx.y.z` 
   incrementing the minor `z` digit

