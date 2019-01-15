#!/usr/bin/env bash

# Expect NISMOD dir as first argument
base_path=$1

# Install xpress
PKGFILE=xp8.4.4_linux_x86_64.tar.gz
SOURCE=$base_path

wget -nc https://clientarea.xpress.fico.com/downloads/8.4.4/xp8.4.4_linux_x86_64_setup.tar -O $SOURCE/xpress.tar --no-check-certificate
tar xf $SOURCE/xpress.tar

INSTALL_TYPE="distrib_client"
XPRESSDIR=/opt/xpressmp

LICPATH=$XPRESSDIR/bin/xpauth.xpr

mkdir $XPRESSDIR/lib/backup 2>/dev/null
mv $XPRESSDIR/lib/libxprl* $XPRESSDIR/lib/backup 2>/dev/null

mkdir -p $XPRESSDIR
if [ "`( gzip -d -c < $PKGFILE | ( cd $XPRESSDIR; tar xf - ) ) 2>&1 | tee -a $SOURCE/error.log`" ]; then
  echo "Errors while extracting the package - your download may be corrupted."
fi

SERVERNAME="ouce-license.ouce.ox.ac.uk"
echo "use_server server=\"$SERVERNAME\"" > $LICPATH

XPRESS_VAR=$XPRESSDIR/bin

# Hack to insert local license
# cp -R $SOURCE/xpauth.xpr $XPRESSDIR/bin/xpauth.xpr

cat > $XPRESSDIR/bin/xpvars.sh << EOF
XPRESSDIR=$XPRESSDIR
XPRESS=$XPRESS_VAR
LD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${LD_LIBRARY_PATH}
DYLD_LIBRARY_PATH=\${XPRESSDIR}/lib:\${DYLD_LIBRARY_PATH}
SHLIB_PATH=\${XPRESSDIR}/lib:\${SHLIB_PATH}
LIBPATH=\${XPRESSDIR}/lib:\${LIBPATH}
PYTHONPATH=\${XPRESSDIR}/lib:\${PYTHONPATH}

CLASSPATH=\${XPRESSDIR}/lib/xprs.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprb.jar:\${CLASSPATH}
CLASSPATH=\${XPRESSDIR}/lib/xprm.jar:\${CLASSPATH}
PATH=\${XPRESSDIR}/bin:\${PATH}

if [ -f "${XPRESSDIR}/bin/xpvars.local.sh" ]; then
  . ${XPRESSDIR}/bin/xpvars.local.sh
fi

export LD_LIBRARY_PATH
export DYLD_LIBRARY_PATH
export SHLIB_PATH
export LIBPATH
export PYTHONPATH
export CLASSPATH
export XPRESSDIR
export XPRESS
EOF

# Makes a template file containing the connection information to
cat > $base_path/template.ini << EOF
[energy_supply]
Description=Energy Supply Data
Driver=PostgreSQL Unicode
Trace=Yes
TraceFile=sql.log
Database=vagrant
Servername=localhost
UserName=vagrant
Password=vagrant
Port=5432
Protocol=6.4
ReadOnly=No
RowVersioning=No
ShowSystemTables=No
ShowOidColumn=No
FakeOidIndex=No
ConnSettings=
EOF

odbcinst -i -l -s -f $base_path/template.ini

#
# Now compile and install the energy_supply model
#

# Read model_version, remote_data, local_dir from config.ini
source <(grep = <(grep -A3 "\[energy-supply\]" $base_path/provision/config.ini))

MODEL_DIR=$base_path/install
DATA_DIR=$base_path/$local_dir
FILENAME=energy_supply_$model_version.zip
MIGRATIONS=$MODEL_DIR/energy_supply/migrations
TMP=$base_path/tmp

mkdir -p $MODEL_DIR
mkdir -p $TMP

python get_data.py /releases/energy_supply/$FILENAME $TMP

rm -r $MODEL_DIR/energy_supply
unzip $TMP/$FILENAME -d $MODEL_DIR && mv -f $MODEL_DIR/energy_supply_$release $MODEL_DIR/energy_supply
rm -r $TMP/$FILENAME

# This is a bit of a hack which places the compiled BIM files into the XPRESS package directory
cp $MODEL_DIR/energy_supply/*.bim $XPRESSDIR/dso

# Run migrations
python $MODEL_DIR/energy_supply/run_migrations.py -r $DATA_DIR/database_minimal $MIGRATIONS

# Setup environment variables on login
echo "source $XPRESSDIR/bin/xpvars.sh" >> $base_path/provision/.bashrc
