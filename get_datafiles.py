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

	# get data files
	with sftp.cd('project/data'):

		# get folder of data
		sftp.get_d('region_definitions')