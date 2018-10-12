# sets up the nismod database
# uses the SFTP server to get datafiles for database

import pysftp, re, subprocess, os
from getpass import getpass

# these details should be pulled from the FTP config file
# ask for SFTP username
username = input("FTP username:")
# ask for SFTP password
password = getpass("Enter password for " + username + ":")

# ask if user want the database to be populated/hydrated automatically
auto_hydrate_db = input("Populate database with data from SFTP (y/n)? ")
if auto_hydrate_db.lower() == 'y' or auto_hydrate_db.lower() == 'yes':
	print("You entered: %s. The API will be installed and the database will be built and populated." %auto_hydrate_db)
	auto_hydrate_db = True
elif auto_hydrate_db.lower() == 'n' or auto_hydrate_db.lower() == 'no':
	print("You entered: %s. The API will be installed and the database built, but not populated." %auto_hydrate_db)
	auto_hydrate_db = False
else:
	# if incorrect input provided, exit setup now and don't run anything
	print("Input incorectly entered - you entered: %s. The API and database will not be setup or populated. Exiting setup." %auto_hydrate_db)
	exit()

# if hydrate db is true, check database exists. if not create it


# set up for sftp connection
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# don't think any of below is needed. all that is required I think is the code to pull the migration files onto the vm
# establish connection to SFTP server
with pysftp.Connection('ceg-itrc.ncl.ac.uk', username=username, password=password, cnopts=cnopts) as sftp:

	# change to directory to database
	with sftp.cd('project/database'):

		# again these files should already be on the vm, loaded by the provision script
		#   maybe change to checking if they are there and if not, pull over
		# get the data folder for the database - contains the base data for the database

		# remove data directory so files can be copied over
		if os.path.isdir('data'):
			subprocess.run(['sudo', 'rm', '-r', 'data/data'])

		# copy database basedata onto vm
		sftp.get_r('data', 'data')

		# this section is still needed, at least for now while migration scripts are on the FTP
		# get provisioning files
		with sftp.cd('nismod-db-vm'):

			# get provision file
			sftp.get('provision-db.sh')

			# run database provision file
			subprocess.run(['sudo', 'sh', 'provision-db.sh'])

			# remove provision file
			subprocess.run(['sudo', 'rm', 'provision-db.sh'])

			# get run migrations file
			sftp.get('run_migrations.py')
			
			# pull migration files
			sftp.get_r('migrations', '')

			# run migrations - down
			subprocess.run(['python3', 'run_migrations.py', 'down'])
			
			# run migrations - up 
			subprocess.run(['python3', 'run_migrations.py', 'up'])
			
			# remove migrations directory
			subprocess.run(['sudo', 'rm', '-r', 'migrations'])
				
			# hydrate database with data is set so
			if auto_hydrate_db:
				# get files to populate database and populate
				sftp.get('database_hydration.py')

				# database hydration through python file
				subprocess.run(['python3', 'database_hydration.py', 'data'])

				# remove hydration file
				subprocess.run(['sudo', 'rm', 'database_hydration.py'])
