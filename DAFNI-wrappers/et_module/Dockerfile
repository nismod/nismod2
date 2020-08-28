FROM docker.pkg.github.com/rosedickinson/nismod2/base-image:latest

WORKDIR /code/nismod2
COPY ./DAFNI-wrappers/et_module/dockerFiles/* /code/nismod2/

CMD python3 job_processing_wrapper.py