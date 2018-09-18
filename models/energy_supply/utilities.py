import os
from collections import namedtuple
from subprocess import check_output

import numpy as np
import psycopg2

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

def parse_season_period(season_period_string):
    """Returns the season and period value from an id
    Argument
    --------
    season_period_string : str
        A string representation of the season_period_id
    Returns
    -------
    tuple
        A tuple of ``(season, period)``
    """
    season, period = season_period_string.split("_")
    season = int(season)
    period = int(period)

    return (season, period)

def get_day(period):
    """Returns the day of the week
    """
    day = ((period - 1) // 24) + 1
    return day

def get_node_numbers():
    """Returns the number of the bus associated with the region
    """
    conn = establish_connection()

    with conn.cursor() as cur:
        sql = """SELECT * from "NodeData";"""
        cur.execute(sql)

        query_results = cur.fetchall()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    bus_numbers = {}
    for row in query_results:
        bus_numbers[row[1]] = row[0]

    return bus_numbers

def _get_bus_numbers():
    """Returns the number of the bus associated with the region
    """
    conn = establish_connection()

    with conn.cursor() as cur:
        sql = """SELECT * from "BusData";"""
        cur.execute(sql)

        query_results = cur.fetchall()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    bus_numbers = {}
    for row in query_results:
        bus_numbers[row[1]] = row[0]

    return bus_numbers

def write_gas_demand_data(data):
    """Writes gas demand data into the database table
    Columns: year, season, day, period (hour), bus number, value
    Arguments
    ---------
    data : list
        A dict of list of SpaceTimeValue tuples
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    node_numbers = _get_node_numbers()

    gas_data = data['gas_demand']
    print("Inserting {} rows of data".format(len(gas_data)))

    sql = """INSERT INTO "GasLoad" (Year, Season, Day, Period, GasNode, GasLoad) VALUES (%s, %s, %s, %s, %s, %s)"""

    it = np.nditer(a, flags=['multi_index'])
    while not it.finished:
        data = it[0]
        region, interval = it.multi_index
        season, period = parse_season_period(interval)

        insert_data = (year,
                       season,
                        day,
                        period,
                        node_number,
                        row.value)

        it.iternext()

        # print("Inserting {} into GasLoad".format(insert_data))
        cur.execute(sql, insert_data)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def write_electricity_demand_data(data):
    """Writes electricity demand data into database table
    Columns: year, season, day, period (hour), bus number, value
    Arguments
    ---------
    data : list
        A list of SpaceTimeValue tuples
    Notes
    -----
    `data` is a list of tuples, which looks something like::
            data > parameter > [SpaceTimeValue(region,
            interval, value) ... ]
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    bus_numbers = _get_bus_numbers()

    elec_data = data['electricity_demand']
    print("Inserting {} rows of data".format(len(elec_data)))

    sql = """INSERT INTO "ElecLoad" (Year, Season, Day, Period, BusNumber, ElecLoad) VALUES (%s, %s, %s, %s, %s, %s)"""
    for row in elec_data:
        season, period = parse_season_period(row.interval)
        day = _get_day(period)
        bus_number = int(bus_numbers[row.region])
        insert_data = (data['timestep'],
                        season,
                        day,
                        period,
                        bus_number,
                        row.value)
        # print("Inserting {} into ElecLoad".format(insert_data))
        cur.execute(sql, insert_data)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

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

    sql = """INSERT INTO "HeatLoad_EH" (year, season, day, period, eh_conn_num, heatload_res, heatload_com) VALUES (%s, %s, %s, %s, %s, %s, %s)"""


    it = np.nditer(data_res, flags=['multi_index'])
    while not it.finished:
        print(it, it.multi_index)
        cell_res = it[0]
        cell_com = data_com[it.multi_index]

        print("Data: %s, %s", cell_res, cell_com)

        region, interval = it.multi_index
        season, day, period = parse_season_day_period(interval)
        insert_data = (year,
                       season,
                       day,
                       period,
                       region,
                       float(cell_res),
                       float(cell_com))

        cur.execute(sql, insert_data)
        it.iternext()

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def get_cooling_water_demand():
    """Calculated cooling water demand as a function of thermal power station operation
    Returns
    -------
    list
        A list of dicts of water demand, with season, period, value
    """
    # Connect to an existing database
    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:

        sql = """SELECT season, period, thermal from "O_Elec_Mix";"""
        cur.execute(sql)

        water_demand = []
        for row in cur.fetchall():
            cooling_water = _calculate_water_demand(row[2])
            water_demand.append({'id': "{}_{}".format(row[0], row[1]),
                                 'water_demand': cooling_water})

    return water_demand


@staticmethod
def _calculate_water_demand(elec_generation):
    """Calculates water demand as a function of electricity generation
    This is a stop-gap, until we calculate water demand in the energy supply
    model
    Arguments
    ---------
    elec_generation : float
        Electricity generation in MWh
    Returns
    -------
    float
        Cooling water demand in ML (million litres)
    """
    COOLING_WATER_DEMAND_ML_PER_MWH = 150 / 10**6
    cooling_water_demand = elec_generation * COOLING_WATER_DEMAND_ML_PER_MWH

    return cooling_water_demand

def get_total_cost():
    """Gets total cost from the objective function table
    Returns
    -------
    total_cost : float
        The total cost in GBP
    """
    # Connect to an existing database
    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        sql = """SELECT objective from "O_Objective";"""
        cur.execute(sql)
        total_cost = cur.fetchone()[0]
    return total_cost

def get_prices():
    """Gets the prices from the O_Prices table
    year integer,
    season integer,
    period integer,
    e_prices double precision
    Returns
    -------
    list
        A list of dicts
    """
    electricity_prices = []

    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        sql = """SELECT season, period, e_prices from "O_Elec_Prices";"""
        cur.execute(sql)

        for row in cur.fetchall():
            electricity_prices.append({'id': "{}_{}".format(row[0], row[1]),
                                        'electricity_price': row[2]})

    return electricity_prices

def get_results():
    """Gets the results as defined in ``outputs.yaml``
    """
    return {'water_demand': get_cooling_water_demand(),
            'total_cost': get_total_cost(),
            'total_emissions': get_total_emissions(),
            'electricity_prices': get_prices()}

def get_model_executable():
    """Return path of ES model executable
    """
    return os.path.join(os.path.dirname(__file__), 'model', 'MISTRAL_ES.exe')

def build_power_station(name, plant_type, region, capacity, build_year,
                        operational_life):
    """Writes a power station into the `GenerationData` table
    Parameters
    ----------
    name : str
        Descriptive name of the power station
    plant_type : int
        The code of the plant type (4 = 'nuclear')
    region : str
        The name of the region
    capacity : float
        The capacity of the power station
    build_year : int
        The year in which the plant is constructed
    technical_lifetime : int
        The lifetime of the plant (used to calculate the retirement year)
    Notes
    -----
    The table schema:
    - gennum integer
    - type integer
    - generatorname character varying(255)
    -  gasnode integer
    - busnum integer
    - minpower double precision
    - maxpower double precision
    - pumpstoragecapacity double precision
    - batterystorage double precision
    - year integer
    - retire integer
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    bus_num = _get_bus_numbers()

    sql = """INSERT INTO "GeneratorData" (type, generatorname, busnum, maxpower, year, retire) VALUES (%s, %s, %s, %s, %s, %s)"""

    data = (plant_type,
            name,
            bus_num[region],
            capacity, build_year,
            build_year + operational_life)

    cur.execute(sql, data)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

def increase_gas_terminal_capacity(terminal_number, capacity_increase):
    """Writes a new gas terminal into the `GasTerminal` table
    Parameters
    ----------
    terminal_number: int
        The number of an existing gas terminal
    capacity_increase: float
        The amount by which the terminal capacity will increase
    Notes
    -----
    The table schema:
    - terminalnumber double precision,
    - year double precision,
    - name character varying(255),
    - gasnode double precision,
    - gasterminaloptcost double precision,
    - terminalcapacity double precision,
    - lngcapacity double precision,
    - intercapacity double precision,
    - domcapacity double precision
    """
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()

    node_num = _get_node_numbers()

    sql = """UPDATE "GasTerminal" SET terminalcapacity=terminalcapacity+(%s) \
                WHERE terminalnumber = (%s)"""

    query_data = (capacity_increase, terminal_number)

    cur.execute(sql, query_data)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def simulate(decisions, state, data):
    """Runs the energy supply model
    Arguments
    ---------
    decisions : list
    state : list
    data : dict
        A dict of lists-of-dicts
    """

    # Write decisions into the input tables
    for decision in decisions:
        if  decision.name == 'nuclear_power_station':
            name = decision.name
            plant_type = decision.data['power_generation_type']['value']
            region = decision.data['location']['value']
            capacity = decision.data['capacity']['value']
            build_year = data['timestep']
            operational_life = decision.data['operational_lifetime']['value']
            build_power_station(name, plant_type, region, capacity,
                                        build_year,
                                        operational_life)
        elif decision.name == 'IOG_gas_terminal_expansion':
            capacity = decision.data['capacity']['value']
            terminal_number = decision.data['gas_terminal_number']['value']
            increase_gas_terminal_capacity(terminal_number, capacity)

    # Write demand data into input tables
    # print(data)
    conn = establish_connection()
    # Open a cursor to perform database operations
    cur = conn.cursor()
    cur.execute("""DELETE FROM "ElecLoad";""")
    cur.execute("""DELETE FROM "GasLoad";""")
    # Make the changes to the database persistent
    conn.commit()
    # Close communication with the database
    cur.close()
    conn.close()

    write_electricity_demand_data(data)
    write_gas_demand_data(data)

    # Run the model
    arguments = [get_model_executable()]
    output = check_output(arguments)

    results = get_results()
    print("Emissions: {}".format(results['total_emissions']))
    print("Total Cost: {}".format(results['total_cost']))
    return results
