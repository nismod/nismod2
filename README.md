# NISMOD v2

NISMOD (National Infrastructure Systems Model) is an integrated model of infrastructure
systems, developed as part of the [ITRC/MISTRAL](https://www.itrc.org.uk/) project.

NISMOD v2 has several components:
- released versions of infrastructure sector models
- an integration framework, [smif](https://smif.readthedocs.io/en/latest/)
- smif configuration to link the models into a system-of-systems model
- smif-compatible scenario, narrative and planning data to run linked model runs
- (for some models) internal model data, used by the model but not exposed to smif as part of
  the system-of-systems configuration

## Setup

To set up NISMOD, first clone this repository, or download a
[release](https://github.com/nismod/nismod2/releases). The directories in this folder contain
or will contain everything required for a model run:
  - `config`: model configuration
  - `data`: (initially incomplete) model data
  - `models`: model wrappers
  - `notebooks`: jupyter notebooks for exploring model results
  - `planning`: decision models
  - `provision`: scripts to install models and get data
  - `results`: (initially empty) for model run results
  - `test`: integration tests
  - `utilities`: helpful scripts to create or migrate configuration

Then either install everything directly:

1. Install smif (recommend using [`conda`](https://conda.io/miniconda.html))
1. Configure connection details for the NISMOD FTP
1. Install models (run `provision/install_*` scripts)
1. Get data (run `provision/get_data_*` scripts)

Or test NISMOD in a virtual machine:

1. Check that you have VirtualBox and Vagrant installed
1. Configure connection details for the NISMOD FTP
1. Setup a virtual machine (run `vagrant up` then connect with `vagrant ssh`)


## Download NISMOD

Download the [latest release](https://github.com/nismod/nismod2/releases/latest) of NISMOD v2.0
from GitHub as a .zip archive and unzip it into a directory.

Alternatively, clone the NISMOD v2.0 repository
from [https://github.com/nismod/nismod2](https://github.com/nismod/nismod2).

```bash
cd path/to/git/projects  # somewhere to keep the nismod project
git clone https://github.com/nismod/nismod2.git
cd nismod2
```

To update NISMOD to the latest development version:

```bash
cd path/to/nismod2    # wherever you cloned the nismod folder
git checkout master  # to make sure you’re on the master branch
git pull             # pull changes from Github to your local machine
```


## Configure connection details for the NISMOD FTP

Add your credentials for the NISMOD FTP server to `provision/ftp.ini` within the
NISMOD folder:

```
[ftp-config]
ftp_server=sage-itrc.ncl.ac.uk
ftp_username=<username>
ftp_password=<password>
```

## Running NISMOD on a virtual machine

The Vagrantfile defines the automated setup for a virtual machine, which will provide a
reproducible development environment.

In virtual machine terminology, the virtual machine (vm for short) is sometimes called the
‘guest’ machine and the physical computer is called the ‘host’ machine.

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

Then results are written to subfolders within the `results` directory.

### Updating

To reload and re-provision the virtual machine after updating NISMOD:

```bash
vagrant reload --provision
```

### Viewing Results

NISMOD includes some experimental jupyter notebooks to help access and view results.

First, start the notebook server in the background with the command:

    vagrant ssh
    cd /vagrant
    jupyter notebook &> /dev/null &

Then navigate in a browser to
[`localhost:8910`](http://localhost:8910/notebooks/Results%20Viewer%20-%20Split%20Out.ipynb)


### Database Connection

Some sector models use a database which runs within the virtual machine and is set up when the
virtual machine is provisioned.

The virtual machine exposes the database on port 6543 on the host machine, so you should be
able to connect with the following details:

| key      | value     |
|----------|-----------|
| Host     | localhost |
| Database | vagrant   |
| User     | vagrant   |
| Password | vagrant   |
| Port     | 6543      |

For example, on the command line, assuming the `psql` postgres command line client is installed
on the host machine, you should be able to connect with:

    psql -d vagrant -h localhost -U vagrant -p 6543


#### Security note

This database setup is intended for testing and development only and assumes that high-numbered
ports are only accessible to the local user. Strong passwords and secure login methods should
be used if the host machine is expected to be accessed by multiple users.


## Development

### General Guidelines

- `master` branch is protected against push and force-push.
- The `master` branch should be treated as live and is used for major releases only
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


## Testing

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


### Gitlab

This git repository is hosted at a second ‘remote’ within the School of Geography. the
ouce-gitlab server (https://gitlab.ouce.ox.ac.uk/NISMOD/nismod2). Changes pushed to the gitlab
remote will trigger a testing pipeline, this will install the nismod2 system and run a series
of tests.

These tests should give feedback on the installation process and perform high level integration
tests that validate dependencies between sector models.


### Gitlab-runner

There is a pool of gitlab-runner workers active that pick up and run jobs on each commit/push.
A local gitlab-runner can be setup using the following configuration.

```
concurrent = 1
check_interval = 0

[[runners]]
  name = "ubuntu-nismod2"
  url = "https://gitlab.ouce.ox.ac.uk/"
  token = "12964bfcd398c966ebf128f1b5b34f"
  executor = "docker"
  [runners.docker]
    tls_verify = false
    image = "ubuntu:xenial"
    privileged = false
    disable_cache = false
    volumes = ["/cache"]
    shm_size = 0
  [runners.cache]
  ```


## Acknowledgements

NISMOD was written and developed by researchers in the Infrastructure Transition Research
Consortium as part of the EPSRC sponsored MISTRAL programme.
