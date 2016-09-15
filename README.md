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

Then on the command line, from this directory, run:

    vagrant up

This will download a virtual machine image and install all the packages and
software which are required to test and run NISMOD onto that virtual machine.
