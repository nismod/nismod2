# sets up the nismod database
# uses the SFTP server to get datafiles for database

import pysftp, re, subprocess, os
from getpass import getpass
from os import listdir as listdir
from os.path import dirname, realpath, join, isfile

def run_migrations(migration_direction):
	"""

	:param direction:
	:return:
	"""
	# get the path of the current directory
	working_path = dirname(realpath(__file__))

	# run migrations given parameter passed
	if migration_direction == 'up':
		ran = up_migrations(working_path)
	elif migration_direction == 'down':
		ran = down_migrations(working_path)


def down_migrations(working_path):
	'''
	Run down migrations to resolve database to blank
	'''

	# run key file to remove foreign keys from database
	file = 'remove-foreign_keys.sql'
	# check file exists
	if isfile(join(working_path, 'migrations', file)):
		# run sql file silently
		subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-f', join(working_path, 'migrations', file)])
	else:
		return False

	# loop through files to remove tables
	for file in listdir(join(working_path, 'migrations')):

		# check if file is a down migration
		if file[0:4] == 'down':
			# run sql file silently
			subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-f', join(working_path, 'migrations', file)])

	return True


def up_migrations(working_path):
	'''
	Run up migrations to build database
	'''

	# declare name of foreign key file
	# run key file to add foreign keys between relations
	fky_file = 'add-foreign_keys.sql'

	# check file exists - if not stop now
	if isfile(join(working_path, 'migrations', fky_file)) is False:
		return False

	# loop through files
	for file in listdir(join(working_path, 'migrations')):

		# check if file is a down migration
		if file[0:2] == 'up':
			# run sql file silently
			subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-f', join(working_path, 'migrations', file)])

	# run key file to add foreign keys between relations
	# run sql file silently
	subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-f', join(working_path, 'migrations', fky_file)])

	return True


def main():
	"""

	:return:
	"""
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

	# pull across migration files, run migrations, delete migration files
	# establish connection to SFTP server
	with pysftp.Connection('ceg-itrc.ncl.ac.uk', username=username, password=password, cnopts=cnopts) as sftp:

		# change directory to database
		with sftp.cd('project/database'):

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

				# run the migrations - down first in case anything exists already

				# run migrations - down
				#subprocess.run(['python3', 'run_migrations.py', 'down'])
				run_migrations('down')

				# run the migrations - up to build the database

				# run migrations - up
				#subprocess.run(['python3', 'run_migrations.py', 'up'])
				run_migrations('up')

				# remove migrations directory
				subprocess.run(['sudo', 'rm', '-r', 'migrations'])

				# populate the database with data

				# hydrate database with data if user said yes to this
				'''if auto_hydrate_db:
					# get files to populate database and populate
					sftp.get('database_hydration.py')
	
					# database hydration through python file
					subprocess.run(['python3', 'database_hydration.py', 'data'])
	
					# remove hydration file
					subprocess.run(['sudo', 'rm', 'database_hydration.py'])
				'''

main()
