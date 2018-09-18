"""Energy supply wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel
from csv import DictReader
import subprocess
import os
import psycopg2
from collections import namedtuple

def read_gas_remap(file_name):
    with open(file_name, 'r') as load_map:
        reader = DictReader(load_map)
        gas_remap = [{'node': int(x['Node']),
                      'eh': int(x['EH_Conn_Num']),
                      'share': x['Load Share'] } for x in reader]

        mapper = {}
        nodes = set()
        for row in gas_remap:
            if row['eh'] in mapper.keys():
                nodes.add(row['node'])
                mapper[int(row['eh'])].update({row['node']: row['share']})
            else:
                nodes.add(row['node'])
                mapper[int(row['eh'])] = {row['node']: row['share']}

        hubs = sorted(mapper.keys())
        return hubs, nodes, mapper


class EnergySupplyWrapper(SectorModel):
    """Energy supply
    """
    def initialise(self, initial_conditions):
        gas_stores = []
        for intervention in initial_conditions:
            if 'intervention_name' in intervention.keys():
                if str(intervention['intervention_name']).startswith('gasstore'):
                    gas_stores.append(intervention)
        build_gas_stores(gas_stores)

    def simulate(self, data):

        nismod_path = os.path.join(os.path.dirname(__file__), "..", "..")
        os.environ["ES_PATH"] = str(os.path.abspath(os.path.join(
            nismod_path, "install", "energy_supply")))

        # Get the current timestep
        now = data.current_timestep
        self.logger.info("Energy supplyWrapper received inputs in %s", now)

        clear_results(now)

        # Get model parameters
        parameter_LoadShed_elec = data.get_parameter('LoadShed_elec')
        self.logger.info('Parameter Loadshed elec: %s', parameter_LoadShed_elec)
        parameter_LoadShed_gas = data.get_parameter('LoadShed_gas')
        self.logger.info('Parameter Loadshed gas: %s', parameter_LoadShed_gas)

        write_load_shed_costs(parameter_LoadShed_elec,
                              parameter_LoadShed_gas)

        # Get model inputs for Heat_EH table
        input_residential_gas_boiler_gas = data.get_data("residential_gas_boiler_gas")
        self.logger.info('Input Residential gas boiler gas: %s',
            input_residential_gas_boiler_gas)

        filepath = os.path.join(
            nismod_path, "data", "energy_supply", "minimal", "_GasLoadMap_minimal.csv")
        hubs, gas_nodes, mapper = read_gas_remap(filepath)

        coefficients = np.zeros((max(hubs), max(gas_nodes)), dtype=float)
        for hub, gas_nodeshare in mapper.items():
            for gas_node, share in gas_nodeshare.items():
                coefficients[hub - 1, gas_node - 1] = share

        reshaped_heat = np.dot(input_residential_gas_boiler_gas.T,
                               coefficients).T
        _, interval_names = self.get_names('residential_gas_boiler_gas')
        region_names = list(gas_nodes)

        self.logger.debug("Writing %s array of shape %s to database",
                          'gasload', reshaped_heat.shape)
        write_input_timestep(
            reshaped_heat,
            'gasload',
            now,
            region_names,
            interval_names)

        input_residential_electricity_boiler_electricity = data.get_data(
            "residential_electricity_boiler_electricity")
        self.logger.info('Input Residential electricity boiler electricity: %s',
            input_residential_electricity_boiler_electricity)

        heatload_inputs = np.array([
            input_residential_gas_boiler_gas,
            input_residential_electricity_boiler_electricity
        ])

        heatload = np.add.reduce(heatload_inputs, axis=0)

        region_names, interval_names = self.get_names(
            'residential_electricity_boiler_electricity')

        write_input_timestep(
            heatload,
            'heatload_res',
            now,
            region_names,
            interval_names)

        # Get model inputs for FuelData table
        input_gas_price = data.get_data("gas_price")
        self.logger.info('Input Gas price: %s', input_gas_price)

        write_gas_price(now, input_gas_price)

        # Run the model
        arguments = [self.get_model_executable()]
        output = subprocess.check_output(arguments,
                                         stderr=subprocess.STDOUT,
                                         shell=True)
        self.logger.info(output)

        # Open database connection
        conn = establish_connection()

        # Retrieve results from Model and write results to data handler
        self.set_results('e_emissions', 'emissions_elec', data, conn, is_annual=True)
        self.set_results('tran_gas_fired', 'tran_gas_fired', data, conn)

        # Close database connection
        conn.close()

        self.logger.info("Energy supplyWrapper produced outputs in %s", now)

    def set_results(self, internal_parameter_name, external_parameter_name, data_handle, conn, is_annual=False):
        """Pass results from database to data handle
        """
        # long way around to get canonical entry names for spatial/temporal resolution
        regions = self.outputs[external_parameter_name].spatial_resolution.get_entry_names()
        intervals = self.outputs[external_parameter_name].temporal_resolution.get_entry_names()

        # read from database - need to be careful with internal vs external param name
        if is_annual:
            output = get_annual_output(conn, internal_parameter_name, data_handle.current_timestep, regions, intervals)
        else:
            output = get_timestep_output(conn, internal_parameter_name, data_handle.current_timestep, regions, intervals)

        # set on smif DataHandle
        data_handle.set_results(external_parameter_name, output)

    def get_names(self, name):
        """Get region and interval names for a given input
        """
        spatial_resolution = self.inputs.get_spatial_res(name).name
        region_names = self.get_region_names(spatial_resolution)
        temporal_resolution = self.inputs.get_temporal_res(name).name
        interval_names = self.get_interval_names(temporal_resolution)

        return region_names, interval_names

    def get_model_executable(self):
        """Return path of current python interpreter
        """
        nismod_dir = os.path.join(os.path.dirname(__file__), '..', '..')
        return os.path.join(nismod_dir, 'install', 'energy_supply' 'Energy_Supply_Master.exe')

    def extract_obj(self, results):
        return 0


def establish_connection():
    """Connect to an existing database
    """
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    return conn

def clear_results(year):
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    sql = """DELETE FROM "output_timestep" WHERE year=%s;"""

    cur.execute(sql, (year,))

    sql = """DELETE FROM "output_annual" WHERE year=%s;"""

    cur.execute(sql, (year,))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def parse_season_day_period(time_id):
    """Returns the season, day and period value from an id

    Argument
    --------
    time_id : int
        An integer representing the interval count
    Returns
    -------
    tuple
        A tuple of ``(season, period)``

    Notes
    -----
    time_id = (168 * (season - 1)) + es_hour + 1
    """
    season = divmod(time_id - 1, 168)
    day, period = divmod(season[1], 24)
    return (season[0] + 1, day + 1, period + 1)

def compute_interval_id(season, day, period):
    """
    Arguments
    ---------
    season : int
    day : int
    period : int

    Returns
    -------
    int

    """
    return 1 + (168 * (season - 1)) + (24 * (day - 1)) + (period - 1)

def write_gas_price(year, data):
    """

    Arguments
    ---------
    year : int
        The current model year
    data : numpy.ndarray
       Price data
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute("""DELETE FROM "FuelData" WHERE "Year"=%s AND "Fuel_ID"=1;""", (year, ))

    sql = """INSERT INTO "FuelData" ("Fuel_ID", "FuelType", "Year", "Season", "FuelCost") VALUES (%s, %s, %s, %s, %s)"""

    it = np.nditer(data, flags=['multi_index'])
    while not it.finished:
        cell = it[0]

        _, interval_index = it.multi_index
        fuel_id = 1
        fueltype = 'Gas'
        insert_data = (fuel_id,
                       fueltype,
                       year,
                       interval_index + 1,
                       float(cell))

        # print("Data: {}".format(insert_data))

        cur.execute(sql, insert_data)
        it.iternext()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def write_rows_into_array(list_of_row_tuples, regions, intervals):
    """Writes query results into a numpy array

    Arguments
    ---------
    list_of_row_tuples : list

    Returns
    -------
    numpy.ndarray

    """
    num_regions = len(regions)
    num_intervals = len(intervals)
    array = np.zeros((num_regions, num_intervals))
    for region, interval, value in list_of_row_tuples:
        if region - 1 >= num_regions:
            raise KeyError("Region %s out of bounds" % region)
        if interval - 1 >= num_intervals:
            raise KeyError("Interval %s out of bounds" % interval)

        array[region - 1, interval - 1] = value
    return array


def get_annual_output(conn, output_parameter, year, regions, intervals):
    """Retrieves annual parameters from the database
    """
    with conn.cursor() as cur:
        sql = """SELECT r.name AS region, '1', o.value AS value
                 FROM "output_annual" AS o
                 INNER JOIN region AS r ON o.region_id = r.id
                 WHERE parameter = %s AND year = %s;"""
        cur.execute(sql, (output_parameter, year))
        try:
            results = write_rows_into_array(cur, regions, intervals)
        except(KeyError) as ex:
            raise KeyError(str(ex) + " in parameter %s" % output_parameter) from ex
    return results


def get_timestep_output(conn, output_parameter, year, regions, intervals):
    """Retrieves parameters with intervals from the database
    """
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        sql = """SELECT o.season, o.day, o.period,
                 r.name AS region, o.value AS value
                 FROM "output_timestep" AS o
                 INNER JOIN region AS r ON o.region_id = r.id
                 WHERE parameter = %s AND year = %s;"""
        cur.execute(sql, (output_parameter, year))

        region_interval_value_generator = (
            (
                row[3],  # region id
                compute_interval_id(int(row[0]), int(row[1]), int(row[2])),  # interval id
                row[4]  # value
            )
            for row in cur
        )
        try:
            results = write_rows_into_array(region_interval_value_generator, regions, intervals)
        except(KeyError) as ex:
            raise KeyError(str(ex) + " in parameter %s" % output_parameter) from ex
    return results


def write_load_shed_costs(loadshedcost_elec,
                          loadshedcost_gas):
    """
    """
    # Connect to an existing database
    conn = establish_connection()

    sql = """INSERT INTO "LoadShedCosts" ("EShedC", "GShedC") VALUES (%s, %s);"""

    print("New loadshed cost values: {}, {}".format(loadshedcost_elec, loadshedcost_gas))

    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute("""DELETE FROM "LoadShedCosts";""")
    with conn.cursor() as cur:
        cur.execute(sql, (loadshedcost_elec, loadshedcost_gas))

    conn.commit()

    conn.close()


def build_gas_stores(gas_stores):
    """Set up the initial system from a list of interventions

    Write in the all interventions with the intervention_name ``gasstore``
    to the GasStore table.

    Arguments
    ---------
    gas_stores : list

    Notes
    -----
    GasStorage" (
        storagenum double precision,
        gasnode double precision,
        name character varying(255),
        year double precision,
        inflowcap double precision,
        outflowcap double precision,
        storagecap double precision,
        outflowcost double precision
    """
    conn = establish_connection()
    cur = conn.cursor()

    cur.execute("""DELETE FROM "GasStorage";""")

    for store in gas_stores:

        sql = """INSERT INTO "GasStorage" ("StorageNum", "GasNode", "Name", "Year", "InFlowCap", "OutFlowCap", "StorageCap", "OutFlowCost") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (store['storagenumber'],
                store['gasnode'],
                store['name'],
                store['build_year'],
                store['inflowcap'],
                store['outflowcap'],
                store['storagecap'],
                store['outflowcost']
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def get_region_mapping(input_parameter_name):
    """Return a dict of database ids from region ids

    Arguments
    ---------
    input_parameter_name : string
        The name of the input parameter

    Returns
    -------
    dict
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute("""SELECT name, id
                        FROM region
                        WHERE regiontype = (
                            SELECT regiontype from input_parameter
                            WHERE name=%s);""",
                    (input_parameter_name, ))
        mapping = cur.fetchall()
    conn.close()

    return dict(mapping)

def write_input_timestep(input_data, parameter_name, year,
                         region_names, interval_names):
    """Writes input data into database table

    Uses the index of the numpy array as a reference to interval and region definitions

    Arguments
    ---------
    input_data : numpy.ndarray
        Residential heating data
    parameter_name : string
        Name of the input parameter

    Notes
    -----
    Database table columns are::

        year
        season
        day
        period
        region_id
        value
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute("""DELETE FROM "input_timestep" WHERE parameter=%s;""", (parameter_name, ))

    sql = """INSERT INTO "input_timestep" (year, season, day, period, region_id, parameter, value) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    print(input_data.shape, region_names)

    region_mapping = get_region_mapping(parameter_name)

    print(region_mapping)

    it = np.nditer(input_data, flags=['multi_index'])
    while not it.finished:
        cell = it[0]

        region, interval = it.multi_index
        season, day, period = parse_season_day_period(int(interval_names[interval]))
        insert_data = (year,
                       season,
                       day,
                       period,
                       region_mapping[int(region_names[region])],
                       parameter_name,
                       float(cell))

        # print("Data: {}".format(insert_data))

        cur.execute(sql, insert_data)
        it.iternext()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()
