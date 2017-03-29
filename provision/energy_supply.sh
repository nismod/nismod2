
# Update package lists
apt-get update
# Install OS packages
apt-get install -y build-essential git vim-nox python3-pip python3 postgresql \
    postgresql-contrib odbc-postgresql unixodbc-dev

# Database config to listen on network connection
sed -i "s/#listen_address.*/listen_addresses 'localhost'/" \
    /etc/postgresql/9.5/main/postgresql.conf
# Create vagrant role if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_user WHERE usename = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "psql -c \"CREATE ROLE vagrant SUPERUSER LOGIN PASSWORD 'vagrant';\" "
# Create vagrant database if not exists
su postgres -c "psql -c \"SELECT 1 FROM pg_database WHERE datname = 'vagrant';\" " \
    | grep -q 1 || su postgres -c "createdb -E UTF8 -T template0 --locale=en_US.utf8 -O vagrant vagrant"

# use ubuntu package to install latest pip
pip install --upgrade pip


# Install xpress
PKGFILE=xp8.1_linux_x86_64.tar.gz

SOURCE=/vagrant

wget -nc https://clientarea.xpress.fico.com/downloads/8.1.0/xp8.1_linux_x86_64_setup.tar -O $SOURCE/xpress.tar --no-check-certificate
tar xf $SOURCE/xpress.tar
# ./install.sh

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
CORRECT_LICENSE=1

echo "" > $XPRESSDIR/bin/xpvars.sh
cat > $XPRESSDIR/bin/xpvars.sh <<EOF
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
cat > /vagrant/template.ini <<EOF
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

odbcinst -i -l -s -f /vagrant/template.ini

# Setup environment
. $XPRESSDIR/bin/xpvars.sh

# Now compile and install the energy_supply model
MODEL_DIR=/vagrant/models/energy_supply/model
cp $MODEL_DIR/Initial.bim $XPRESSDIR/dso/Initial.bim

# Compile the energy_supply model
cd $MODEL_DIR
make clean
make

cd /vagrant

# Run migrations
su vagrant -c "python /vagrant/models/energy_supply/db/run_migrations.py -u"

# Setup environment variables on login
echo "source /opt/xpressmp/bin/xpvars.sh" >> /home/vagrant/.bashrc
