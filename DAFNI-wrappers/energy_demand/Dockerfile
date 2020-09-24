FROM docker.pkg.github.com/nismod/nismod2/base-image:latest

WORKDIR /code/nismod2
COPY ./DAFNI-wrappers/energy_demand/dockerFiles/* /code/nismod2/

CMD python3 job_processing_wrapper.py