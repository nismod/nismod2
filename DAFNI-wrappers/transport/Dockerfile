FROM docker.pkg.github.com/nismod/nismod2/base-image:latest

# Setup environment variables
ENV JAVA_OPTS -Xmx4g \
    _JAVA_OPTIONS -Xmx4g

WORKDIR /code
RUN mkdir -p /code/nismod2/install/transport /usr/share/man/man1 \
&&  apt-get update \
&&  apt-get --fix-broken install \
    gcc-8-base \
    default-jre \
    rxvt-unicode \
    openjdk-11-jre-headless \
    openjdk-11-jre \
    openjdk-11-jdk \
    maven -y

RUN git clone https://github.com/nismod/transport.git

WORKDIR /code/transport/transport
RUN sed -i "s/\${skip.unit.tests}/true/g" ./pom.xml \
&&  mvn clean install -U
RUN ls -la /code/transport/transport/target \
&&  mv /code/transport/transport/target/transport-2.3.0.jar /code/nismod2/install/transport/transport.jar 

WORKDIR /code/nismod2
COPY ./DAFNI-wrappers/transport/dockerFiles/* /code/nismod2/

CMD python3 job_processing_wrapper.py