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

		# get region_definitions
		sftp.get_r('region_definitions', 'data/region_definitions')

		# get initial_conditions
		sftp.get_r('initial_conditions', 'data/initial_conditions')

		# get interventions
		sftp.get_r('interventions', 'data/interventions')

		# get interval_definitions
		sftp.get_r('interval_definitions', 'data/interval_definitions')

		# get narratives
		sftp.get_r('narratives', 'data/narratives')

		# get scenarios
		sftp.get_r('scenarios', 'data/scenarios')
