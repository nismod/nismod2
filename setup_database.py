# sets up the nismod database
# uses the SFTP server to get datafiles for database

import pysftp, re, subprocess
from getpass import getpass

# ask for SFTP username
username = input("Username:")
# ask for SFTP password
password = getpass("Enter password for " + username + ":")

cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

# establish connection to SFTP server
with pysftp.Connection('ceg-itrc.ncl.ac.uk', username=username, password=password, cnopts=cnopts) as sftp:

	# get api wheel
	with sftp.cd('project/database'):

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

				# end search
				break

	# get database files

