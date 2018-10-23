import os, sys, subprocess, yaml, json
import psycopg2
from psycopg2.extras import DictCursor
from psycopg2 import sql


def get_value_from_dict(dictionary, key):
	"""Attempt to get value from a dictionary
	"""

	if key in dictionary.keys():
		value = dictionary[key]
		return value
	else:
		return ''


def add_to_value_string(value, value_string):
	"""

	:param value:
	:param vaule_string:
	:return:
	"""
	# if set as true, add value to list and column name to list
	add_column = True

	# form value list
	if isinstance(value, str):  # if value a string
		value_string += "'%s'," % (value)
	elif isinstance(value, list):  # if value a list
		text = str(value).replace('[', '{').replace(']', '}')
		value_string += "'%s'," % (text)
	elif value is None:  # if value is NoneType
		add_column = False
	else:  # if value is anything else eg. a number
		value_string += "%s," % (value)

	return value_string, add_column


class HydrateDatabase:

	def __init__(self, db_connection, db_cursor):
		self.db_connection = db_connection
		self.db_cursor = db_cursor

	def get_sector_id(self, sector_name):
		"""

		:param sector_name:
		:return:
		"""

		# get sector id from sectors relation
		self.db_cursor.execute('SELECT id FROM sectors WHERE name=%s', [sector_name])

		# get query result
		sector_id = self.db_cursor.fetchone()

		# if sector not found, return an error
		if sector_id is None:
			return False

		return sector_id[0]

	def check_sector_intervention_relation_exists(self, sector_name):
		"""

		:param sector_name:
		:return:
		"""
		# get names of relations in database
		self.db_cursor.execute('SELECT table_name FROM information_schema.tables WHERE table_schema = \'public\' AND table_type = \'BASE TABLE\';')
		table_names = self.db_cursor.fetchall()

		# check if intervention relation exists
		for table in table_names:
			if 'interventions_%s' % sector_name in table[0]:
				# return to the interventions function if the table exists
				return

		table_name = 'interventions_'+sector_name
		# if sector interventions relation does not exist
		self.db_cursor.execute(sql.SQL('CREATE TABLE {} (id serial, sector integer, name varchar, type integer, details varchar);').format(sql.Identifier(table_name)))
		self.db_connection.commit()

		return

	def check_column_exists(self, relation_name, column_key):
		"""

		:param relation_name:
		:param column_key:
		:return:
		"""

		# get column names for relation
		self.db_cursor.execute('SELECT column_name FROM information_schema.columns WHERE 	table_schema = \'public\' AND table_name = %s;', [relation_name])
		column_names = self.db_cursor.fetchall()

		# loop through column names
		for column_name in column_names:
			# check text for column in column name
			if column_key.lower() == column_name[0]:
				# if column exists, return
				return

		# add new column to relation
		# work out column datatype - this needs changing
		column_datatype = 'varchar'

		# run add column sql
		self.db_cursor.execute(sql.SQL('ALTER TABLE {0} ADD COLUMN {1} {2}').format(sql.Identifier(relation_name), sql.Identifier(column_key.lower()), sql.Identifier(column_datatype)))
		self.db_connection.commit()

		return

	def add_intervention(self, intervention, sector_id, sector_name):
		"""

		:param intervention:
		:param sector_id:
		:param sector_name:
		:param relation_name:
		:return:
		"""
		# relation_name
		relation_name = 'interventions_' + sector_name

		### add intervention to the interventions relation
		# get intervention name - what happens if no such key?
		intervention_name = None
		for key in intervention.keys():
			if key == 'name':
				intervention_name = intervention['name']

		if intervention_name is None:
			intervention_name = ''

		# get the intervention details
		intervention_details = str(intervention)

		# run insert statement to add intervention
		self.db_cursor.execute('INSERT INTO interventions (sector, name, details) VALUES (%s,%s,%s)',
							   [sector_id, intervention_name, intervention_details])

		### add to the sector specific interventions relation
		# check if a interventions relation for the sector exists
		self.check_sector_intervention_relation_exists(sector_name)

		# get column list from yml
		# get value list
		column_list = ''
		value_list = ''
		fields = ''

		# loop through the keys for the intervention
		for key in intervention.keys():

			# check if an attribute, or if a dictionary with sub-attributes
			if isinstance(intervention[key], dict):
				# loop through the sub-attributes
				for subkey in intervention[key].keys():

					# form value list
					value_list, add_column = add_to_value_string(intervention[key][subkey], value_list)

					# form column list
					if add_column is True:
						column_list += "%s," % (str(key) + '_' + str(subkey))
						#fields += sql.Identifier(str(key) + '_' + str(subkey))

						# check for column name and add them if missing
						self.check_column_exists(relation_name, (str(key) + '_' + str(subkey)))
			else:
				# form value list
				value_list, add_column = add_to_value_string(intervention[key], value_list)

				# form column list
				if add_column is True:
					column_list += "%s," % key
					#fields += sql.Identifier(key)

					# check for column name and add them if missing
					self.check_column_exists(relation_name, key)

		# check if intervention type is in the types table - if not add
		# this will need updating depending on what format the initial conditions will be uploaded in
		#subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-c',	'INSERT INTO intervention_type (name) SELECT (\'%s\') WHERE NOT EXISTS (SELECT id FROM intervention_type WHERE name=\'%s\');' % (intervention['name'], intervention['name'])])
		# insert intervention into interventions table - get intervention type id and add to table
		# subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-c','INSERT INTO %s (%s,sector,intervention_type_id) VALUES (%s,(SELECT id FROM sectors WHERE name=\'%s\'),(SELECT id FROM intervention_type WHERE name=\'%s\'));' % ('interventions_'+sector_name,column_list[:-1], value_list[:-1], sector_name, intervention['name'])])
		subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c',	'INSERT INTO %s (%s, sector) VALUES (%s,%s);' % ('interventions_' + sector_name, column_list[:-1], value_list[:-1], sector_id)])
		#self.db_cursor.execute(sql.SQL('INSERT INTO {0} ({1}, {2}) VALUES (%s,%s);').format(sql.Identifier(relation_name), fields.join(','), sql.Identifier('sector')), [value_list[:-1], sector_id])
		#self.db_connection.commit()
		return

	def region_definitions(self, data_dir):
		'''
		imports regions into database
		'''
		# set location to search for data
		dir_name = 'region_definitions'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir, dir_name))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is a file skip it
			if os.path.isfile(os.path.join(data_dir, dir_name, item)):
				continue

			# add the directory as a region set
			subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c', 'INSERT INTO region_sets (name) VALUES (\'%s\');' % (item)])

		return

	def interval_definitions(self, data_dir):
		'''
		Insert into the interval_sets and interval tables any interval data within the interval_definitions folder
		'''
		# set location to search for data
		dir_name = 'interval_definitions'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir, dir_name))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is not a file skip it
			if os.path.isfile(os.path.join(data_dir, dir_name, item)) is False:
				continue

			# need to read the first line of the file to get the column order
			file = open(os.path.join(data_dir, dir_name, item))
			columns = file.readline().replace('\n', '').split(',')

			# create a comma separated string of column order
			file_columns = ''
			for col in columns:
				file_columns += '"%s",' % (col)

			# get name to be used in database
			name = item.split('.')[0]

			# add the file as an interval set using the file name returning the id of the set
			self.db_cursor.execute('INSERT INTO interval_sets (name) VALUES (%s) RETURNING id;', [name.replace("'",'')])
			self.db_connection.commit()
			set_id = self.db_cursor.fetchone()[0]

			# create temporary table to copy data into, copy data into temp table, copy data from temp to full table with id from the interval_sets table
			subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c',
							'CREATE TEMPORARY TABLE intervals_temp ("id" varchar, "start" varchar, "end" varchar); COPY intervals_temp(%s) FROM \'%s\' DELIMITER \',\' CSV	HEADER; INSERT INTO intervals SELECT "id","start","end",(SELECT id FROM interval_sets WHERE name = \'%s\' LIMIT 1) FROM intervals_temp;' % (file_columns[:-1], os.path.join('/vagrant', data_dir, dir_name, item), name)])

		return

	def interventions(self, data_dir):
		"""
		import interventions into the database
		two step procedure
		  (1) add to the interventions relation (for quick access)
		  (2) add to the interventions_sector relation (for detailed queries)
				- for each attribute check a column exists & if not add
		"""
		# set location to search for data
		dir_name = 'interventions'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir, dir_name))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is not a file skip it
			if os.path.isfile(os.path.join(data_dir, dir_name, item)) is False:
				continue

			# open yml file and get data
			with open(os.path.join(data_dir, dir_name, item), 'r') as stream:
				data = yaml.load(stream)

			# get sector name
			sector_name = item.split('.')[0]
			if 'interventions' in sector_name:
				sector_name = sector_name.replace('_interventions', '')

			# get the sector id
			sector_id = self.get_sector_id(sector_name)

			# if error returned
			if sector_id is False:
				print('could not add data to database - file origin was: %s' % os.path.join(data_dir, dir_name, item))
				continue

			# loop through the interventions
			for intervention in data:

				# add an intervention to the database
				self.add_intervention(intervention, sector_id, sector_name)

		return

	def initial_conditions(self, data_dir):
		"""
		populated tables with the initial conditions data (initial interventions?)
		populates the interventions table
			- each file equates to a set
			- the set should be added to interventions_planned
			- should use the interventions function
		"""
		# set location to search for data
		dir_name = 'initial_conditions'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir, dir_name))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is not a file skip it
			if os.path.isfile(os.path.join(data_dir, dir_name, item)) is False:
				continue

			# open yml file and get data
			with open(os.path.join(data_dir, dir_name, item), 'r') as stream:
				data = yaml.load(stream)

			# get sector name
			sector_name = item.split('.')[0]
			sector_name = sector_name.rsplit('_',1)[0]
			# get sector id
			sector_id = self.get_sector_id(sector_name)

			# if error returned
			if sector_id is False:
				print('could not add data to database - file origin was: %s' % os.path.join(data_dir, dir_name, item))
				continue

			# need to get the id of the interventions where they are added
			# at the moment this doesn't happen so:
			# - get the value of the serial before added, and then after
			# then create set

			# get value of serial in interventions relation
			self.db_cursor.execute('SELECT id FROM interventions ORDER BY id desc LIMIT 1;')
			first_id = self.db_cursor.fetchone()[0] + 1

			# loop through the conditions
			for intervention in data:
				self.add_intervention(intervention, sector_id, sector_name)

			# get value of serial in interventions relation
			self.db_cursor.execute('SELECT id FROM interventions ORDER BY id desc LIMIT 1;')
			last_id = self.db_cursor.fetchone()[0]

			# generate list of id's for set
			id_range = []

			while first_id <= last_id:
				id_range.append(first_id)
				first_id += 1
			id_range = str(id_range).replace('[','{').replace(']','}')

			# insert set details into interventions set relation
			self.db_cursor.execute('INSERT INTO intervention_sets (interventions, sector, name, description) VALUES (%s,%s,%s,%s);', ['%s' % id_range, sector_id, item, 'Initial conditions'])
			self.db_connection.commit()

		return

	def sos_models(self, data_dir):
		"""Populate sos model relations
		"""

		# set location to search for data
		dir_name = 'sos_models'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir, dir_name))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is not a file skip it
			if os.path.isfile(os.path.join(data_dir, dir_name, item)) is False:
				continue

			# open yml file and get data
			with open(os.path.join(data_dir, dir_name, item), 'r') as stream:
				data = yaml.load(stream)

				# get values for each sos model
				name = get_value_from_dict(data, 'name')
				description = get_value_from_dict(data, 'description')
				max_iterations = get_value_from_dict(data, 'max_iterations')
				convergence_absolute_tolerance = get_value_from_dict(data, 'convergence_absolute_tolerance')
				convergence_relative_tolerance = get_value_from_dict(data, 'convergence_relative_tolerance')

				# varchar arrays
				dependencies = json.dumps(get_value_from_dict(data, 'dependencies')) # as nested dict, converted to json
				narrative_sets = get_value_from_dict(data, 'narrative_sets')
				scenario_sets = get_value_from_dict(data, 'scenario_sets')

				sector_models = data['sector_models']

				# these are stored as varchar arrays - need to be set as lists if not present in file
				if dependencies == '':
					dependencies = []
				if narrative_sets == '':
					narrative_sets = []
				if scenario_sets == '':
					scenario_sets = []

				# query to insert sos model into the database
				self.db_cursor.execute(
					'INSERT INTO sos_models (name, description, sector_models, dependencies, narrative_sets, scenario_sets, max_iterations, convergence_absolute_tolerance, convergence_relative_tolerance) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;',
					[name, description, sector_models, dependencies, narrative_sets, scenario_sets, max_iterations,
					 convergence_absolute_tolerance, convergence_relative_tolerance])
				self.db_connection.commit()

				# get result from query
				sos_model_id = self.db_cursor.fetchone()

				# if nothing returned, return an error
				if sos_model_id is None:
					return False

				return True


	def base_data_hydration(self, data_dir):
		'''
		add base data to database
		'''
		# set location to search for data
		dir_name = 'data'

		# get list of files in directory
		dir_contents = os.listdir(os.path.join(data_dir))

		# if no files, return to main function
		if len(dir_contents) == 0: return

		# loop through the directory
		for item in dir_contents:

			# if item is not a file skip it
			if os.path.isfile(os.path.join(data_dir, item)) is False:
				continue

			# hydrate with units file
			if item == 'units.txt':
				file = open(os.path.join(data_dir, item))

				# get name of file - also name of table
				name = item.split('.')[0]

				# insert into table line by line
				# read each line in file
				for line in file:
					# split the line on the first '=' s
					unit, description = line.split('=', 1)
					subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c',
									'INSERT INTO %s (unit, description) VALUES (\'%s\',\'%s\');' % (
										name, unit, description)])

			elif item == 'sectors.txt':
				file = open(os.path.join(data_dir, item))

				# get name of file - also name of table
				name = item.split('.')[0]

				# insert into table line by line
				# read each line in file
				for line in file:
					# split the line on the first '=' s
					subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c',
									'INSERT INTO %s (name) VALUES (\'%s\');' % (
										name, line.strip())])

			else:
				# need to read the first line of the file to get the column order
				file = open(os.path.join(data_dir, item))
				columns = file.readline().replace('\n', '').split(',')

				# create a comma separated string of column order
				file_columns = ''
				for col in columns:
					file_columns += '"%s",' % (col)

				# get name of file - also name of table
				name = item.split('.')[0]

				# copy data to database table
				subprocess.run(['psql', '-U', 'vagrant', '-d', 'nismod_smif', '-q', '-c',
								'COPY %s(%s) FROM \'%s\' DELIMITER \',\' CSV	HEADER;' % (
								name, file_columns[:-1], os.path.join('/vagrant', data_dir, item))])

		return


def main():
	'''
	Data_path: should be the location where all the data for populating the database is stored.
	It should match the defined structure.
	--data_path
		|--initial_conditions
			|--file1.yml
			|--file2.yml
	    |--interval_definitions
	    	|--file1.csv
	    	|--file2.csv
	    |--interventions
	    	|--file1.yml
	    	|--file2.yml
	    |--narratives
	    |--region_definitions
			|--region_set_1
			|--region_set_2
	    |--scenarios
	    |--data
	    	|--file1.csv
	    	|--file2.csv

	'''
	# get data path from passed arguments
	data_path = sys.argv[1]
	config_data_path = 'config'

	# create database connection and cursor
	db_connection = psycopg2.connect("host=localhost dbname=nismod_smif user=vagrant password=vagrant")
	db_cursor = db_connection.cursor(cursor_factory=psycopg2.extras.DictCursor)

	# run database hydration for base database data
	HydrateDatabase(db_connection, db_cursor).base_data_hydration(data_path)

	# run database hydration for region definitions
	# only reads in the file names at the moment
	HydrateDatabase(db_connection, db_cursor).region_definitions(data_path)

	# run database hydration for interval definitions
	HydrateDatabase(db_connection, db_cursor).interval_definitions(data_path)

	# run database hydration for interventions
	HydrateDatabase(db_connection, db_cursor).interventions(data_path)

	# run database hydration for initial conditions
	HydrateDatabase(db_connection, db_cursor).initial_conditions(data_path)

	# run database hydration for sos_models
	HydrateDatabase(db_connection, db_cursor).sos_models(config_data_path)

	# close database connection
	db_connection.close()

main()