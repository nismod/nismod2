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
        gas_stores = []
        for intervention in initial_conditions:
            if 'intervention_name' in intervention.keys():
                if str(intervention['intervention_name']).startswith('gasstore'):
                    gas_stores.append(intervention)
        build_gas_stores(gas_stores)


    def simulate(self, data):

        # Get the current timestep
        now = data.current_timestep
        self.logger.info("Energy supplyWrapper received inputs in %s", now)

        # Get model parameters
        parameter_LoadShed_elec = data.get_parameter('LoadShed_elec')
        self.logger.info('Parameter Loadshed elec: %s', parameter_LoadShed_elec)
        
        parameter_LoadShed_gas = data.get_parameter('LoadShed_gas')
        self.logger.info('Parameter Loadshed gas: %s', parameter_LoadShed_gas)

        write_load_shed_costs(parameter_LoadShed_elec, 
                              parameter_LoadShed_gas)
        
        # Get model inputs
        input_residential_gas_boiler_gas = data.get_data("residential_gas_boiler_gas")
        self.logger.info('Input Residential gas boiler gas: %s', 
            input_residential_gas_boiler_gas)
        
        input_residential_electricity_boiler_electricity = data.get_data("residential_electricity_boiler_electricity")
        self.logger.info('Input Residential electricity boiler electricity: %s', 
            input_residential_electricity_boiler_electricity)
        
        input_residential_gas_stirling_micro_CHP = data.get_data("residential_gas_stirling_micro_CHP")
        self.logger.info('Input Residential gas stirling micro chp: %s', input_residential_gas_stirling_micro_CHP)
        
        input_residential_electricity_heat_pumps_electricity = data.get_data("residential_electricity_heat_pumps_electricity")
        self.logger.info('Input Residential electricity heat pumps electricity: %s', input_residential_electricity_heat_pumps_electricity)
        
        input_residential_electricity_district_heating_electricity = data.get_data("residential_electricity_district_heating_electricity")
        self.logger.info('Input Residential electricity district heating electricity: %s', input_residential_electricity_district_heating_electricity)
        
        input_residential_gas_district_heating_gas = data.get_data("residential_gas_district_heating_gas")
        self.logger.info('Input Residential gas district heating gas: %s', input_residential_gas_district_heating_gas)
        
        input_residential_gas_non_heating = data.get_data("residential_gas_non_heating")
        self.logger.info('Input Residential gas non heating: %s', input_residential_gas_non_heating)
        
        input_residential_electricity_non_heating = data.get_data("residential_electricity_non_heating")
        self.logger.info('Input Residential electricity non heating: %s', input_residential_electricity_non_heating)
        
        input_service_gas_boiler_gas = data.get_data("service_gas_boiler_gas")
        self.logger.info('Input Service gas boiler gas: %s', input_service_gas_boiler_gas)
        
        input_service_electricity_boiler_electricity = data.get_data("service_electricity_boiler_electricity")
        self.logger.info('Input Service electricity boiler electricity: %s', input_service_electricity_boiler_electricity)
        
        input_service_gas_stirling_micro_CHP = data.get_data("service_gas_stirling_micro_CHP")
        self.logger.info('Input Service gas stirling micro chp: %s', input_service_gas_stirling_micro_CHP)
        
        input_service_electricity_heat_pumps_electricity = data.get_data("service_electricity_heat_pumps_electricity")
        self.logger.info('Input Service electricity heat pumps electricity: %s', input_service_electricity_heat_pumps_electricity)
        
        input_service_electricity_district_heating_electricity = data.get_data("service_electricity_district_heating_electricity")
        self.logger.info('Input Service electricity district heating electricity: %s', input_service_electricity_district_heating_electricity)
        
        input_service_gas_district_heating_gas = data.get_data("service_gas_district_heating_gas")
        self.logger.info('Input Service gas district heating gas: %s', input_service_gas_district_heating_gas)
        
        input_service_gas_non_heating = data.get_data("service_gas_non_heating")
        self.logger.info('Input Service gas non heating: %s', input_service_gas_non_heating)
        
        input_service_electricity_non_heating = data.get_data("service_electricity_non_heating")
        self.logger.info('Input Service electricity non heating: %s', input_service_electricity_non_heating)
        
        input_industry_gas_boiler_gas = data.get_data("industry_gas_boiler_gas")
        self.logger.info('Input Industry gas boiler gas: %s', input_industry_gas_boiler_gas)
        
        input_industry_electricity_boiler_electricity = data.get_data("industry_electricity_boiler_electricity")
        self.logger.info('Input Industry electricity boiler electricity: %s', input_industry_electricity_boiler_electricity)
       
        input_industry_biomass_boiler_biomass = data.get_data("industry_biomass_boiler_biomass")
        self.logger.info('Input Industry biomass boiler biomass: %s', input_industry_biomass_boiler_biomass)
        
        input_industry_gas_stirling_micro_CHP = data.get_data("industry_gas_stirling_micro_CHP")
        self.logger.info('Input Industry gas stirling micro chp: %s', input_industry_gas_stirling_micro_CHP)
    
        input_industry_electricity_heat_pumps_electricity = data.get_data("industry_electricity_heat_pumps_electricity")
        self.logger.info('Input Industry electricity heat pumps electricity: %s', input_industry_electricity_heat_pumps_electricity)
    
        input_industry_electricity_district_heating_electricity = data.get_data("industry_electricity_district_heating_electricity")
        self.logger.info('Input Industry electricity district heating electricity: %s', input_industry_electricity_district_heating_electricity)
    
        input_industry_gas_district_heating_gas = data.get_data("industry_gas_district_heating_gas")
        self.logger.info('Input Industry gas district heating gas: %s', input_industry_gas_district_heating_gas)
    
        input_industry_biomass_district_heating_biomass = data.get_data("industry_biomass_district_heating_biomass")
        self.logger.info('Input Industry biomass district heating biomass: %s', input_industry_biomass_district_heating_biomass)
    
        input_industry_gas_non_heating = data.get_data("industry_gas_non_heating")
        self.logger.info('Input Industry gas non heating: %s', input_industry_gas_non_heating)
    
        input_industry_electricity_non_heating = data.get_data("industry_electricity_non_heating")
        self.logger.info('Input Industry electricity non heating: %s', input_industry_electricity_non_heating)
    
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
         

        # Sum all inputs ready for writing to tables

        heatload_res_inputs = np.array([
            input_residential_gas_boiler_gas,
            input_residential_electricity_boiler_electricity,
            input_residential_gas_stirling_micro_CHP,
            input_residential_electricity_heat_pumps_electricity,
            input_residential_electricity_district_heating_electricity,
            input_residential_gas_district_heating_gas
            ])
        heatload_res = np.add.reduce(heatload_res_inputs, axis=0)

        heatload_com_inputs = np.array(
            [input_service_gas_boiler_gas,
            input_service_electricity_boiler_electricity,
            input_service_gas_stirling_micro_CHP,
            input_service_electricity_heat_pumps_electricity,
            input_service_electricity_district_heating_electricity,
            input_service_gas_district_heating_gas]
        )
        heatload_com = np.add.reduce(heatload_com_inputs, axis=0)

        gasload_non_heat_res = input_residential_gas_non_heating
        elecload_non_heat_res = input_residential_electricity_non_heating
        gasload_non_heat_com = input_service_gas_non_heating
        elecload_non_heat_com = input_service_electricity_non_heating

        elecload_tran_inputs = np.array(
            [input_industry_electricity_boiler_electricity,
            input_industry_electricity_heat_pumps_electricity,
            input_industry_electricity_district_heating_electricity,
            input_industry_electricity_non_heating])

        elecload_tran = np.add.reduce(elecload_tran_inputs, axis=0)

        gasload_eh_input = np.array(
           [input_industry_gas_boiler_gas,
            input_industry_biomass_boiler_biomass,
            input_industry_gas_stirling_micro_CHP,
            input_industry_gas_district_heating_gas,
            input_industry_biomass_district_heating_biomass,
            input_industry_gas_non_heating]
        )

        # These gasload values are provided at the energy hub regions,
        # but must be mapped to gas nodes using provided gas load map
        gasload_eh = np.add.reduce(gasload_eh_input, axis=0)
        gasload_tran = remap_gas(gasload_eh, gas_map)

        region_names, interval_names = self.get_names(data, "residential_electricity_non_heating")
        write_input_timestep(elecload_non_heat_res, "elecload_non_heat_res", 
                             now, region_names, interval_names)
        region_names, interval_names = self.get_names(data, "service_electricity_non_heating")
        write_input_timestep(elecload_non_heat_com, "elecload_non_heat_com", 
                             now, region_names, interval_names)
        write_input_timestep(elecload_tran, "elecload", 
                             now, region_names, interval_names)
        write_input_timestep(gasload_non_heat_res, "gasload_non_heat_res", 
                             now, region_names, interval_names)
        write_input_timestep(gasload_non_heat_com, "gasload_non_heat_com", 
                             now, region_names, interval_names)
        write_input_timestep(gasload_tran, "gasload", 
                             now, region_names, interval_names)
        write_input_timestep(heatload_res, "heatload_res", 
                             now, region_names, interval_names)
        write_input_timestep(heatload_com, "heatload_com", 
                             now, region_names, interval_names)

        def get_model_executable(self):
            """Return path of current python interpreter
            """
            executable = '/vagrant/models/energy_supply/test/MISTRAL_ES.exe'

            return os.path.join(executable)

        # Run the model
        arguments = [self.get_model_executable()]
        print(check_output(arguments))


        # This results mapping maps output_parameters to sectormodel output names
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
            'load_shed_elec': 'elec_load_shed'}

        annual_results = {
            'total_opt_cost': 'total_opt_cost',
            'emissions_elec': 'e_emissions'}

        # Write timestep results to data handler
        for model_output, parameter in timestep_results.items():
            data.set_results(model_output, get_timestep_output(parameter))
        
        # Write annual results to data handler
        for parameter in annual_results.items():
            data.set_results(parameter, get_annual_output(parameter))

        self.logger.info("Energy supplyWrapper produced outputs in %s", now)

    def extract_obj(self, results):
        return 0

    def get_names(self, data_handle, name):

        spatial_resolution = self.inputs.get_spatial_res(name).name
        region_names = self.get_region_names(spatial_resolution)
        temporal_resolution = self.inputs.get_temporal_res(name).name
        interval_names = self.get_interval_names(temporal_resolution)
        return region_names, interval_names

def establish_connection():
    """Connect to an existing database
    """
    conn = psycopg2.connect("dbname=vagrant user=vagrant")
    return conn

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

    cur.execute("""DELETE FROM "FuelData" WHERE year=%s AND fuel_id=1;""", (year, ))

    sql = """INSERT INTO "FuelData" (fuel_id, fueltype, year, season, fuelcost) VALUES (%s, %s, %s, %s, %s)"""

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

def write_annual_rows_into_array(list_of_row_tuples):
    """Writes annual query results into a numpy array

    Arguments
    ---------
    list_of_row_tuples : list

    Returns
    -------
    numpy.ndarray

    """
    regions = []
    intervals = []
    values = []

    for row in list_of_row_tuples:
        regions.append(int(row[0]))
        intervals.append(int(row[1]))
        values.append(float(row[2]))

    array = np.zeros((len(regions), len(intervals)))
    for region, interval, value in zip(regions, intervals, values):
        array[region - 1, interval - 1] = value
    return array

def write_timestep_rows_into_array(list_of_row_tuples):
    """Writes timestep query results into a numpy array

    Arguments
    ---------
    list_of_row_tuples : list

    Returns
    -------
    numpy.ndarray

    """
    regions = []
    intervals = []
    values = []

    for row in list_of_row_tuples:
        regions.append(int(row[3]))
        intervals.append(compute_interval_id(int(row[0]), 
                                             int(row[1]), 
                                             int(row[2])))
        values.append(float(row[4]))

    array = np.zeros((len(regions), len(intervals)))
    for region, interval, value in zip(regions, intervals, values):
        array[region - 1, interval - 1] = value
    return array


def get_annual_output(output_parameter):
    """Retrieves annual parameters from the database
    """
    # Connect to an existing database
    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        sql = """SELECT r.name AS region, '1', o.value AS value
                 FROM "output_annual" AS o
                 INNER JOIN region AS r ON o.region_id = r.id
                 WHERE parameter = %s;"""
        cur.execute(sql, (output_parameter, ))
        results = cur.fetchall()

    conn.close()

    return write_annual_rows_into_array(results)


def get_timestep_output(output_parameter):
    """
    """
    # Connect to an existing database
    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        sql = """SELECT o.season, o.day, o.period, 
                 r.name AS region, o.value AS value
                 FROM "output_timestep" AS o
                 INNER JOIN region AS r ON o.region_id = r.id
                 WHERE parameter = %s;"""
        cur.execute(sql, (output_parameter, ))
        results = cur.fetchall()

    conn.close()

    return write_timestep_rows_into_array(results)


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

def write_input_timestep(input_data, parameter_name, year):
    """Writes input data into database table 
    
    Uses the index of the numpy array as a reference to interval and region definitions
    
    Arguments
    ---------
    input_data : numpy.ndarray
        Residential heating data
    parameter_name : string
        Name of the input parameter
    year : integer
        The year for which the data needs to be written

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

    region_mapping = get_region_mapping(parameter_name)

    it = np.nditer(input_data, flags=['multi_index'])
    while not it.finished:
        cell = it[0]

        region, interval = it.multi_index
        season, day, period = parse_season_day_period(interval + 1))
        insert_data = (year,
                       season,
                       day,
                       period,
                       region_mapping[region + 1],
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