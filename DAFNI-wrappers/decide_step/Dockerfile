FROM docker.pkg.github.com/rosedickinson/nismod2/base-image:latest

WORKDIR /code/nismod2
COPY ./DAFNI-wrappers/decide_step/dockerFiles/* /code/nismod2/

CMD python3 job_processing_wrapper.py