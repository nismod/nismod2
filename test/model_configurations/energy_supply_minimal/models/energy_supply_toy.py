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

    def simulate(self, data):

        # Get the current timestep
        now = data.current_timestep
        self.logger.info("Energy supplyWrapper received inputs in %s", now)

        # Get model parameters
        parameter_LoadShed_elec = data.get_parameter('LoadShed_elec')
        self.logger.info('Parameter Loadshed elec: %s', parameter_LoadShed_elec)
        
        parameter_LoadShed_gas = data.get_parameter('LoadShed_gas')
        self.logger.info('Parameter Loadshed gas: %s', parameter_LoadShed_gas)
        
        # Get model inputs for Heat_EH table
        input_residential_gas_boiler_gas = data.get_data("residential_gas_boiler_gas")
        self.logger.info('Input Residential gas boiler gas: %s', 
            input_residential_gas_boiler_gas)
        
        input_residential_electricity_boiler_electricity = data.get_data("residential_electricity_boiler_electricity")
        self.logger.info('Input Residential electricity boiler electricity: %s', 
            input_residential_electricity_boiler_electricity)
    
        input_gas_price = data.get_data("gas_price")
        self.logger.info('Input Gas price: %s', input_gas_price)

        # heatload_eh_inputs = np.array([
        #     input_residential_gas_boiler_gas,
        #     input_residential_electricity_boiler_electricity]
        #     )

        write_heat_demand_data(
            now, 
            input_residential_gas_boiler_gas,
            input_residential_electricity_boiler_electricity)

        heatload_eh = np.add.reduce(heatload_eh_inputs, axis=0)

        print(heatload_eh)

        # Write results to data handler
        data.set_results("emissions_elec", None)

        self.logger.info("Energy supplyWrapper produced outputs in %s", now)

    def extract_obj(self, results):
        return 0


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

def write_heat_demand_data(year, data_res, data_com):
    """Writes heat demand data into database table
    
    Arguments
    ---------
    year : int
        The current model year
    data_res : numpy.ndarray
        Residential heating data
    data_com : numpy.ndarray
        Commercial heating data

    Notes
    -----
    Columns are::

        year
        season
        day
        period
        eh_conn_num
        heatload_res
        heatload_com
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    cur.execute("""DELETE FROM "HeatLoad_EH" WHERE year=%s;""", [year])

    sql = """INSERT INTO "HeatLoad_EH" (year, season, day, period, eh_conn_num, heatload_res, heatload_com) VALUES (%s, %s, %s, %s, %s, %s, %s)"""


    it = np.nditer(data_res, flags=['multi_index'])
    while not it.finished:
        cell_res = it[0]
        cell_com = data_com[it.multi_index]

        region, interval = it.multi_index
        season, day, period = parse_season_day_period(interval + 1)
        insert_data = (year,
                       season,
                       day,
                       period,
                       region + 1,
                       float(cell_res),
                       float(cell_com))

        # print("Data: {}".format(insert_data))

        cur.execute(sql, insert_data)
        it.iternext()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()
