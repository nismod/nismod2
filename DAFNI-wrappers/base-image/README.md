# Base Image

This is the base Docker image for all the other DAFNI-wrappers for NISMOD2 models. This
image contains all of the packages and scripts that are common between the models.

The settings.py file sets some commonly used paths and also grabs the parameters from
the environment variables that DAFNI sets on the container when the Model is run. This
is how users can specify the parameter values via Workflows.

utils.py just contains some useful functions that are used by the wrapper scripts.

run_nismod.py contains the code that actually runs the NISMOD2 model based on the
parameters the user provided.

job_processing_wrapper.py is the script DAFNI calls to run the models, it simply calls
run_nismod.py and then copies the results of the model into the proper output location.

You shouldn't need to build this image locally in order to build the other models as
they all use the image in the github registry as their base.
