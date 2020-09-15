FROM docker.pkg.github.com/rosedickinson/nismod2/base-image:latest

ENV PYTHONUNBUFFERED=0 \
    XPRESS_DIR=/opt/xpressmp \
    XPRESS=/opt/xpressmp/bin \
    PGPASSWORD=postgres \
    PGHOST=0.0.0.0 \
    PGUSER=postgres \
    PGPORT=5432 \
    PGDATABASE=postgres
ENV PATH="/opt/conda/envs/nismod/bin:$XPRESS:$PATH" \
    LD_LIBRARY_PATH="$XPRESS_DIR/lib:$LD_LIBRARY_PATH" \
    DYLD_LIBRARY_PATH="$XPRESS_DIR/lib:$DYLD_LIBRARY_PATH" \
    SHLIB_PATH="$XPRESS_DIR/lib:$SHLIB_PATH" \
    LIBPATH="$XPRESS_DIR/lib:$LIBPATH" \
    PYTHONPATH="$XPRESS_DIR/lib:$PYTHONPATH" \
    CLASSPATH="$XPRESS_DIR/lib/xprs.jar:$XPRESS_DIR/lib/xprb.jar:$XPRESS_DIR/lib/xprm.jar:$CLASSPATH"

RUN apt-get update \
&&  apt-get install \
    postgresql-11 \
    postgresql-client-11 \
    postgresql-contrib-11 \
    unixodbc-dev \
    odbc-postgresql -y

WORKDIR /code
# Download Fico Xpress for Energy supply
RUN wget https://clientarea.xpress.fico.com/downloads/8.5.10/xp8.5.10_linux_x86_64_setup.tar -O /code/xp8.5.10_linux_x86_64_setup.tar
