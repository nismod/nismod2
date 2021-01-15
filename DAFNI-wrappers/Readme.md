# DAFNI Wrappers

These are the Docker images that wrap the NISMOD2 models to allow them to be run on
DAFNI.

Each of the images has their own readme file. Here are just some things to keep in mind
when changing the images:

- The extract_data.py scripts currently do reference the data packs by file name
  directly so if you update the data packs you will also need to update the
  extract_data.py scripts to make sure they are correct too.
- The decide_step and transforms wrappers define their own run_nismod.py script that
  overwrites the one in the base image, this means any changes to the script in the base
  image won't apply to those wrappers.
