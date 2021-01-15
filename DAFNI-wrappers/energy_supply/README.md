# energy_supply

The DAFNI wrapper for NISMOD2's energy_supply model. This model is quite complex, the
current setup on DAFNI has the postgres database running in a sidecar (a container that
runs along side the main model container but that is linked by a local network). The
image for this sidecar is in the db folder, unfortunately DAFNI doesn't currently have a
good process to allow users to customise and specify sidecars themselves so this image
is provided purely for completeness and to allow you to run the model locally.

I have separated out the model image into a new model_base image (which adds packages to
the generic base image) and the model image which actually containers the wrapper
scripts. I have done this because the install for FICO and the other packages in the
model_base image takes a long time and also because these are unlikely to ever change.
The model image itself is quite simple, it contains the wrapper scripts and a built
version of the energy supply model. The model and the datasets will be extracted to the
right places and the model will then be run.

I have provided a docker-compose file that should allow you to build and run the energy
supply locally with minimal hassle.

One thing that hasn't been included in the repository is the license file for FICO that
this wrapper needs in order to run the energy supply model. You will unfortunately have
to provide this yourself as FICO is commercial software.
