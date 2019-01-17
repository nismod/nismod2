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

Then in outline (more details further below) either install everything directly to run nismod
on a desktop, server or cluster:

1. Install smif (recommend using [`conda`](https://conda.io/miniconda.html))
1. Install model dependencies:
   - FICO XPRESS (for energy supply)
   - Java (for transport)
   - PostgreSQL and ODBC (for energy supply)
1. Configure:
   - connection details for the NISMOD FTP (copy `template.ftp.ini` to `ftp.ini` and edit)
   - connection details for a Postgres database (copy `template.dbconfig.ini` to
     `dbconfig.ini` and edit for your database)
1. Install models (run `provision/install_*` scripts)
1. Get data (run `provision/get_data_*` scripts)

Or set up a virtual machine for testing:

1. Check that you have VirtualBox and Vagrant installed
1. Configure:
   - connection details for the NISMOD FTP (copy `template.ftp.ini` to `ftp.ini` and edit)
   - connection details for a Postgres database (copy `template.dbconfig.ini` to
     `dbconfig.ini`)
   - FICO XPRESS license (copy `template.xpauth.xpr` or your own license to `xpauth.xpr`)
1. Setup a virtual machine (run `vagrant up` then connect with `vagrant ssh`)

### Download NISMOD

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
cd path/to/nismod2   # wherever you cloned the nismod folder
git checkout master  # to make sure you’re on the master branch
git pull             # pull changes from Github to your local machine
```

### Configure connection details for the NISMOD FTP

Within the NISMOD folder, copy `provision/template.ftp.ini` to `provision/ftp.ini` and add your
credentials to connect to the NISMOD FTP server:

```
[ftp-config]
ftp_host=sage-itrc.ncl.ac.uk
ftp_username=username
ftp_password=password
```

### Configure connection details for a Postgres database

Within the NISMOD folder, copy `provision/template.dbconfig.ini` to `provision/dbconfig.ini`
and edit to connect to your database.

If you intend to use the vagrant virtual machine with the database as provisioned by default,
leave the details unchanged.

```
[energy-supply]
dbname=vagrant
host=localhost
user=vagrant
password=vagrant
port=5432
```

### Configure FICO XPRESS license

If you will install FICO XPRESS manually, skip this step.

Within the NISMOD folder, copy `provision/template.xpauth.xpr` to `provision/xpauth.xpr`.

If you are running within the University of Oxford OUCE network, the license server should be
available and no changes are necessary. Otherwise, set the value to connect to your local
license server or replace this file with a license file provided by FICO support (contact via
https://www.fico.com)

```
use_server server="ouce-license.ouce.ox.ac.uk"
```


## Running NISMOD on desktop/server/cluster

To run NISMOD directly, you will need to install smif, model dependencies and models.

The `provision/vm_provision.sh` script may be a useful point of reference, as it is run by the
root user within the virtual machine (on Ubuntu 16.04) to automate the same process.

### Install smif

See [installation instructions](https://smif.readthedocs.io/en/latest/installation.html) for
full details.

The recommended method uses [`conda`](https://conda.io/miniconda.html)):

```bash
conda config --add channels conda-forge  # enable the conda-forge channel, required for smif
conda create --name nismod python=3.6 smif  # create a conda environment for nismod
conda activate nismod  # activate the nismod conda environment
```

### Install model dependencies

#### FICO XPRESS (for energy supply)

See [energy supply documentation](https://github.com/nismod/energy_supply#downloading-and-installation-of-the-package)
for full details.

On Linux (x64) it should be possible download and install FICO by running:

```bash
mkdir xpress_setup
wget -nc -qO- \
  "https://clientarea.xpress.fico.com/downloads/8.4.4/xp8.4.4_linux_x86_64_setup.tar" \
  --no-check-certificate | tar -C xpress_setup -xv
./xpress_setup/install.sh
```

#### Java (for transport)

See [transport model documentation](https://github.com/nismod/transport) for full details.

To run the transport model, it should be sufficient to have the [Java Runtime Environment (JRE)
version 8](https://www.oracle.com/technetwork/java/javase/downloads/jre8-downloads-2133155.html)
installed.

On Ubuntu, run:

```bash
sudo apt update && sudo apt install default-jre
```

#### PostgreSQL and ODBC (for energy supply)

See [energy supply documentation](https://github.com/nismod/energy_supply#downloading-and-installation-of-the-package)
for full details.

The energy supply model connects to a [Postgres](https://www.postgresql.org/) database via
ODBC, so requires access to a Postgres server, an ODBC installation and the Postgres ODBC
drivers.

On Ubuntu, install Postgres, libpq (shared library for postgres clients), ODBC
and postgres connector:

```bash
sudo apt update && sudo apt install \
  postgresql postgresql-contrib \
  libpq-dev \
  unixodbc-dev odbc-postgresql
```

### Get data

Add the NISMOD FTP server to your known hosts:

```bash
# Check NISMOD FTP host
ssh-keyscan sage-itrc.ncl.ac.uk
# output should match:
# sage-itrc.ncl.ac.uk ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC/TVt0ajA0VAM97SA1+ZM6j6W43Mnysnl1SOwUB7e8YYBwAKvOdO4GJx5EBytYK1gcwcG8VK2uo81OomkkLX+M67GiaDJi9ziF0YclroVaYfrMqgBvjK7NM5Ae1ahLThNzFsIVNHnHeuCe4l2/d7Z2jJHo7ruD3cPpersJD3CiW4pI992VKtifnc4We9ZM/Ol263TP6PktMQBdNRpsec/3qh80//+Ftz4g0zbc/Zyo/R5SxzMLSMaBmZZ2WTDRPRVMGRQbqllRRkJCrLt9ngs3A6TGga95dbvGnjZWQZalnxbRUVsZNQQ9jYljLRXpS/f3I5+PuO+yiMD/FOBPLvtJ
# add to known hosts
ssh-keyscan sage-itrc.ncl.ac.uk >> ~/.ssh/known_hosts
```

Install `pysftp`: `pip install pysftp`.

Run each of the `provision/get_data_*` scripts:

```bash
bash ./provision/get_data_digital_comms.sh .
bash ./provision/get_data_energy_demand.sh .
bash ./provision/get_data_energy_suppy.sh .
bash ./provision/get_data_transport.sh .
```

### Install models

Run each of the `provision/install_*` scripts:

```bash
bash ./provision/install_digital_comms.sh .
bash ./provision/install_energy_demand.sh .
bash ./provision/install_energy_suppy.sh .
bash ./provision/install_transport.sh .
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

Create and configure the guest machine, running this command from the NISMOD directory:

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

### Accessing services from outside the virtual machine

It is possible to connect to some services running in the guest virtual machine directly from
the host. Vagrant is set to automatically forward some ports.

#### Viewing Results

NISMOD includes some experimental jupyter notebooks to help access and view results.

First, start the notebook server in the background with the command:

    vagrant ssh
    cd /vagrant
    jupyter notebook &> /dev/null &

Then navigate in a browser to
[`localhost:8910`](http://localhost:8910/notebooks/Results%20Viewer%20-%20Split%20Out.ipynb)

#### Database Connection

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

##### Security note

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

Continuous integration testing is currently available through a GitLab server based in the
School of Geography in Oxford. You can access the [project on OUCE
GitLab](https://gitlab.ouce.ox.ac.uk/NISMOD/nismod2) and [monitor
jobs](https://gitlab.ouce.ox.ac.uk/NISMOD/nismod2/-/jobs) through the web interface.

To add the remote and push a branch for automated testing, run:

```bash
git remote add ouce https://gitlab.ouce.ox.ac.uk/NISMOD/nismod2.git
git checkout feature/branch
git push -u ouce
```

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
