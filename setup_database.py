# sets up the nismod database
# uses the SFTP server to get datafiles for database

import pysftp, re, subprocess, os
from getpass import getpass

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


cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# establish connection to SFTP server
with pysftp.Connection('ceg-itrc.ncl.ac.uk', username=username, password=password, cnopts=cnopts) as sftp:

	# change to directory to database
	with sftp.cd('project/database'):

		# get api wheel

		# get list of files
		file_names = sftp.listdir()

		# find wheel file
		for file in file_names:
			wheel = re.search(".whl", file)

			# when found, get from server
			if wheel:
				sftp.get(file)

				# install api from wheel file
				subprocess.run(['sudo', 'pip3', 'install', file])

				# following install, delete wheel
				subprocess.run(['sudo', 'rm', file])

				# end search for file
				break

		# get the data folder for the database - contains the base data for the database
			
		# remove data directory so files can be copied over
		if os.path.isdir('data'):
			subprocess.run(['sudo', 'rm', '-r', 'data/data'])

		# copy database basedata onto vm
		sftp.get_r('data', 'data')

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
