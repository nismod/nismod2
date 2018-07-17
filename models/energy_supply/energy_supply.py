"""Energy supply wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel
from subprocess import check_output
import os
import psycopg2
from collections import namedtuple


class EnergySupplyWrapper(SectorModel):
    """Energy supply
    """

    def initialise(self, initial_conditions):
        pass

    def before_model_run(self, data):
        pass

    def simulate(self, data):
        """Run the energy supply operational simulation
        """
        # Get the current timestep
        now = data.current_timestep
        clear_results(now)
        write_simduration(now)
        self.get_model_parameters(data)

        self.clear_input_tables()

        self.build_interventions(data)
        self.get_model_inputs(data, now)
        self.run_the_model()
        self.retrieve_outputs(data, now)

    def get_model_parameters(self, data):
        # Get model parameters
        parameter_LoadShed_elec = data.get_parameter('LoadShed_elec')
        self.logger.info('Parameter Loadshed elec: %s', parameter_LoadShed_elec)
        
        parameter_LoadShed_gas = data.get_parameter('LoadShed_gas')
        self.logger.info('Parameter Loadshed gas: %s', parameter_LoadShed_gas)

        write_load_shed_costs(parameter_LoadShed_elec, 
                              parameter_LoadShed_gas)

    def clear_input_tables(self):
        """Removes all state data from database tables

        Removes data from:
        - GeneratorData
        - WindPVData_EH
        - WindPVData_Tran
        - GasStorage
        """
        delete_from("GeneratorData")
        delete_from("WindPVData_EH")
        delete_from("WindPVData_Tran")
        delete_from("GasStorage")

    def build_interventions(self, data):
        # Build interventions
        state = data.get_state()
        self.logger.info("Current state: %s", state)
        current_interventions = self.get_current_interventions(state)
        print([ci.name for ci in self.interventions])
        print([ci['name'] for ci in current_interventions])
        retirees = []
        generators = []
        distributors = []
        gas_stores = []

        for intervention in current_interventions:
            self.logger.info(intervention)
            if intervention['table_name'] == 'GeneratorData':
                if intervention['retire']:
                    retirees.append(intervention)
                else:
                    generators.append(intervention)
            elif str(intervention['name']).startswith('gasstore'):
                gas_stores.append(intervention)
            else:
                distributors.append(intervention)

        self.logger.info('Writing %s gas stores to database', len(gas_stores))
        build_gas_stores(gas_stores)
        self.logger.info('Building %s generators', len(generators))
        build_generator(generators)
        self.logger.info('Building %s distributed generators', len(distributors))    
        build_distributed(distributors)
        self.logger.info('Retiring %s generators', len(retirees))
        retire_generator(retirees)

    def get_model_inputs(self, data, now):
        # Get model inputs
        self.logger.info("Energy Supply Wrapper received inputs in %s", now)
        input_residential_gas_non_heating = data.get_data("residential_gas_non_heating")
        self.logger.info('Input Residential gas non heating: %s', input_residential_gas_non_heating)
        
        input_residential_electricity_non_heating = data.get_data("residential_electricity_non_heating")
        self.logger.info('Input Residential electricity non heating: %s', input_residential_electricity_non_heating)
        
        input_service_gas_non_heating = data.get_data("service_gas_non_heating")
        self.logger.info('Input Service gas non heating: %s', input_service_gas_non_heating)
        
        input_service_electricity_non_heating = data.get_data("service_electricity_non_heating")
        self.logger.info('Input Service electricity non heating: %s', input_service_electricity_non_heating)
            
        input_cost_of_carbon = data.get_data("cost_of_carbon")
        self.logger.info('Input Cost of carbon: %s', input_cost_of_carbon)
    
        input_electricity_price = data.get_data("electricity_price")
        self.logger.info('Input Electricity price: %s', input_electricity_price)
    
        input_gas_price = data.get_data("gas_price")
        self.logger.info('Input Gas price: %s', input_gas_price)
    
        input_nuclearFuel_price = data.get_data("nuclearFuel_price")
        self.logger.info('Input Nuclearfuel price: %s', input_nuclearFuel_price)
    
        input_oil_price = data.get_data("oil_price")
        self.logger.info('Input Oil price: %s', input_oil_price)
    
        input_coal_price = data.get_data("coal_price")
        self.logger.info('Input Coal price: %s', input_coal_price)
         
        heatload_res = data.get_data('residential_heatload')
        self.logger.info('Residential heatload: %s', heatload_res)

        heatload_com = data.get_data('service_heatload')
        self.logger.info('Service heatload: %s', heatload_com)

        gasload_non_heat_res = input_residential_gas_non_heating
        elecload_non_heat_res = input_residential_electricity_non_heating
        gasload_non_heat_com = input_service_gas_non_heating
        elecload_non_heat_com = input_service_electricity_non_heating

        region_names, interval_names = self.get_names( "residential_electricity_non_heating")
        self.logger.info('Writing %s to database', "elecload_non_heat_res")
        write_input_timestep(elecload_non_heat_res, "elecload_non_heat_res", 
                             now, region_names, interval_names)
        region_names, interval_names = self.get_names( "service_electricity_non_heating")
        self.logger.info('Writing %s to database', "elecload_non_heat_com")
        write_input_timestep(elecload_non_heat_com, "elecload_non_heat_com", 
                             now, region_names, interval_names)
        self.logger.info('Writing %s to database', "gasload_non_heat_res")
        write_input_timestep(gasload_non_heat_res, "gasload_non_heat_res", 
                             now, region_names, interval_names)
        self.logger.info('Writing %s to database', "gasload_non_heat_com")
        write_input_timestep(gasload_non_heat_com, "gasload_non_heat_com", 
                             now, region_names, interval_names)
        self.logger.info('Writing %s to database', "heatload_res")
        write_input_timestep(heatload_res, "heatload_res", 
                             now, region_names, interval_names)
        self.logger.info('Writing %s to database', "heatload_com")
        write_input_timestep(heatload_com, "heatload_com", 
                             now, region_names, interval_names)

        elecload_tran = data.get_data('elecload')
        self.logger.info('Writing %s to database', "elecload")
        write_input_timestep(elecload_tran, "elecload", 
                             now, region_names, interval_names)

        gasload = data.get_data('gasload')
        region_names, interval_names = self.get_names( "gasload")
        self.logger.info('Writing %s to database', "gasload")
        write_input_timestep(gasload, "gasload", 
                             now, region_names, interval_names)


    def run_the_model(self):
        """Run the model
        """
        os.environ["ES_PATH"] = "/vagrant/install/energy_supply"
        self.logger.info("\n\n***Running the Energy Supply Model***\n\n")
        arguments = [self.get_model_executable()]
        self.logger.info(check_output(arguments))

    def retrieve_outputs(self, data, now):
        """Retrieves results from the model
        
        This results mapping maps output_parameters to sectormodel output names
        external => internal
        """
        timestep_results = {
            'gasfired_gen_tran': 'tran_gas_fired',
            'coal_gen_tran': 'tran_coal',
            'pumpedHydro_gen_tran': 'tran_pump_power',
            'hydro_gen_tran': 'tran_hydro',
            'nuclear_gen_tran': 'tran_nuclear',
            'interconnector_elec_tran': 'tran_interconnector',
            'renewable_gen_tran': 'tran_renewable',
            'elec_cost': 'e_price',
            'elec_reserve_tran': 'e_reserve',
            'domestic_gas': 'gas_domestic',
            'lng_supply': 'gas_lng',
            'interconnector_gas': 'gas_interconnector',
            'storage_gas': 'gas_storage',
            'wind_gen_tran': 'tran_wind_power',
            'pv_gen_tran': 'tran_pv_power',
            'wind_curtail_tran': 'tran_wind_curtailed',
            'pv_curtail_tran': 'tran_pv_curtailed',
            'gasfired_gen_eh': 'eh_gas_fired',
            'wind_gen_eh': 'eh_wind_power',
            'pv_gen_eh': 'eh_pv_power',
            'heat_gasboiler': 'eh_gas_boiler',
            'heat_heatpump': 'eh_heat_pump',
            'load_shed_gas': 'gas_load_shed',
            'load_shed_elec': 'elec_load_shed',
            'load_shed_gas_eh': 'gas_load_shed_eh',
            'load_shed_elec_eh': 'elec_load_shed_eh',
            'emissions_eh': 'e_emissions_eh',
            'emissions_bb': 'e_emissions'}

        annual_results = {
            # 'total_opt_cost': 'total_opt_cost',
            # 'emissions_elec': 'e_emissions'
            }

        # Open database connection
        conn = establish_connection()

        # Write timestep results to data handler
        for external_name, internal_name in timestep_results.items():
            self.set_results(internal_name, external_name, data, conn)

        # Write annual results to data handler
        for external_name, internal_name in annual_results.items():
            self.set_results(internal_name, external_name, data, conn, is_annual=True)

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
        executable = '/vagrant/install/energy_supply/Energy_Supply_Master.exe'

        return os.path.join(executable)

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

def write_simduration(year):
    """
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("""DELETE FROM "SimDuration";""")

    sql = """INSERT INTO "SimDuration" ("TimeStep", "Year", "Seasons", "Days", "Periods") VALUES (%s, %s, %s, %s, %s);"""

    cur.execute(sql, ('1', year, '4', '7', '24'))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

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

    cur.execute("""DELETE FROM "FuelData" WHERE year=%s AND fuel_id=1;""", (year, ))

    sql = """INSERT INTO "FuelData" (fuel_id, fueltype, year, season, fuelcost) VALUES (%s, %s, %s, %s, %s);"""

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
    
def retire_generator(plants):
    conn = establish_connection()
    cur = conn.cursor()

    for plant in plants:

        sql = """DELETE FROM "GeneratorData" WHERE "GeneratorName"=%s"""

        cur.execute(sql, (str(plant['name']), ))

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close() 

def build_generator(plants):
    """Writes an intervention into the GeneratorData table

    Arguments
    ---------
    plants : list
    """
    conn = establish_connection()
    cur = conn.cursor()

    for plant in plants:

        if 'EH' in plant['name']:

            sql = """INSERT INTO "GeneratorData" ("Type", "GeneratorName", "EH_Conn_Num","MinPower", "MaxPower", "Year", "Retire", "SysLayer") VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"""

        elif 'bus' in plant['name']:

            sql = """INSERT INTO "GeneratorData" ("Type", "GeneratorName",  "BusNum", "MinPower", "MaxPower", "Year", "Retire", "SysLayer") VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""

        data = (plant['type'],
                plant['name'],
                plant['location'],
                plant['min_power']['value'],
                plant['capacity']['value'],
                plant['build_year'],
                float(plant['build_year']) + float(plant['operational_lifetime']['value']),
                plant['sys_layer']
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def get_distributed_eh(location, year):

    sql =  """SELECT "OnshoreWindCap", "OffshoreWindCap", "PvCapacity" FROM "WindPVData_EH" WHERE "EH_Conn_Num"=%s AND "Year"=%s;"""

    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute(sql, (location, year))    
        mapping = cur.fetchone()
    conn.close()
    print(mapping)
    return mapping

def get_distributed_tran(location, year):

    sql =  """SELECT "OnshoreWindCap", "OffshoreWindCap", "PvCapacity" FROM "WindPVData_Tran" WHERE "BusNum"=%s AND "Year"=%s;"""

    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute(sql, (location, year))    
        mapping = cur.fetchone()
    conn.close()
    print(mapping)
    return mapping

def build_distributed(plants):
    """Writes a list of interventions into the WindPVData_* table

    Arguments
    ---------
    plants : list
    """
    conn = establish_connection()
    cur = conn.cursor()

    plant_remap = {x: {'build_year': 0, 
                       'offshore': 0, 
                       'onshore': 0, 
                       'pv': 0,
                       'table_name': ''} 
                   for x in range(1, 30)}

    for plant in plants:
        location = int(plant['location'])
        if location in plant_remap:
            plant_remap[location]['build_year'] = plant['build_year']
            plant_remap[location]['table_name'] = plant['table_name']
            if 'offshore' in plant['name']:
                plant_remap[location]['offshore'] =  plant['capacity']['value']
            elif 'onshore' in plant['name']:
                plant_remap[location]['onshore'] = plant['capacity']['value']
            elif 'pv' in plant['name']:
                plant_remap[location]['pv'] = plant['capacity']['value']


    for location, plant in plant_remap.items():

        on = 0
        off = 0
        pv = 0

        if plant['table_name'] == 'WindPVData_EH':
            # sql = """INSERT INTO "WindPVData_EH" ("EH_Conn_Num", "Year", "OnshoreWindCap", "OffshoreWindCap", "PvCapacity") VALUES (%s, %s, %s, %s, %s)"""
            sql = """UPDATE "WindPVData_EH" SET "OnshoreWindCap" = (%s), "OffshoreWindCap" = (%s), "PvCapacity"= (%s) WHERE "EH_Conn_Num"=(%s) AND "Year"=(%s);"""

            previous = get_distributed_eh(location, plant['build_year'])
            if previous:
                on, off, pv = previous
        else:
            # sql = """INSERT INTO "WindPVData_Tran" ("BusNum", "Year", "OnshoreWindCap", "OffshoreWindCap","PvCapacity") VALUES (%s, %s, %s, %s, %s)"""
            sql = """UPDATE "WindPVData_Tran" SET "OnshoreWindCap" = (%s), "OffshoreWindCap" = (%s), "PvCapacity"= (%s) WHERE "BusNum"=(%s) AND "Year"=(%s);"""

            previous = get_distributed_tran(location, plant['build_year'])
            if previous:
                on, off, pv = previous

        data = (
                on + plant['onshore'],
                off + plant['offshore'],
                pv + plant['pv'],
                location,
                plant['build_year'])

        print("Updating location {} into table {}".format(location, plant['table_name']))

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def delete_from(table_name):
    conn = establish_connection()
    cur = conn.cursor()

    sql = '''DELETE FROM "''' + table_name + '''";'''
    cur.execute(sql)
    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
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

        sql = """INSERT INTO "GasStorage" ("StorageNum", "GasNode", "Name", "Year", "InFlowCap", "OutFlowCap", "StorageCap", "OutFlowCost") VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""

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

    cur.execute("""DELETE FROM "input_timestep" WHERE parameter=%s AND year=%s;""", (parameter_name, year))

    sql = """INSERT INTO "input_timestep" (year, season, day, period, region_id, parameter, value) VALUES (%s, %s, %s, %s, %s, %s, %s)"""

    region_mapping = get_region_mapping(parameter_name)

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