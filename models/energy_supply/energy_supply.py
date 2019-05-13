"""Energy supply wrapper
"""
import os
from configparser import ConfigParser
from subprocess import check_output

import numpy as np
import psycopg2
import psycopg2.extras
from smif.model.sector_model import SectorModel


try:
    from pyinstrument import Profiler  # import to enable profiling
except ImportError:
    pass


def profile(func):
    """Decorator - add to a function to profile cpu usage (requires pyinstrument):

        @profile
        def method_to_profile():
            ...

    """
    def wrapper(*args, **kwargs):
        profiler = Profiler()
        profiler.start()
        func(*args, **kwargs)
        profiler.stop()
        print(profiler.output_text(unicode=False, color=True))
    return wrapper


class EnergySupplyWrapper(SectorModel):
    """Energy supply
    """

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

        self.build_interventions(data, now)
        self.get_model_inputs(data)
        self.run_the_model()
        self.retrieve_outputs(data, now)

    def get_model_parameters(self, data):
        # Get model parameters
        load_shed_elec = float(data.get_parameter('LoadShed_elec').as_ndarray())
        self.logger.debug('Parameter Loadshed elec: %s', load_shed_elec)

        load_shed_gas = float(data.get_parameter('LoadShed_gas').as_ndarray())
        self.logger.debug('Parameter Loadshed gas: %s', load_shed_gas)

        heat_technology_mode = int(data.get_parameter('heat_mode').as_ndarray())
        self.logger.debug('Parameter heat mode: %s', heat_technology_mode)

        operation_mode = int(data.get_parameter('operation_mode').as_ndarray())
        self.logger.debug('Parameter operation mode: %s', operation_mode)

        with establish_connection() as conn:
            write_load_shed_costs(load_shed_elec, load_shed_gas, conn)
            write_flags(heat_technology_mode,operation_mode, conn)

        conn.close()


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
        delete_from("PipeData")
        delete_from("LineData")
        delete_from("HeatTechData")

    def build_interventions(self, data, current_timestep):
        # Build interventions
        current_interventions = data.get_current_interventions()

        retirees = []
        generators = []
        dist_eh = []
        dist_tran = []
        gas_stores = []
        pipes = []
        lines = []
        gasterminal = []
        heattech = []

        for name, intervention in current_interventions.items():
            intervention['name'] = name
            if intervention['table_name'] == 'GeneratorData':
                if name.split("_")[-1] == 'retire':
                    retirees.append(intervention)
                else:
                    generators.append(intervention)
            elif intervention['table_name'] == 'GasStorage':
                gas_stores.append(intervention)
            elif intervention['table_name'] == 'GasTerminal':
                gasterminal.append(intervention)
            elif intervention['table_name'].startswith('WindPVData_EH'):
                dist_eh.append(intervention)
            elif intervention['table_name'].startswith('WindPVData_Tran'):
                dist_tran.append(intervention)
            elif intervention['table_name'] == 'PipeData':
                pipes.append(intervention)
            elif intervention['table_name'] == 'LineData':
                lines.append(intervention)
            elif intervention['table_name'] == 'HeatTechData':
                heattech.append(intervention)
            else:
                print("Not sure what to do with {}".format(name))

        self.logger.debug("Writing %s pipes to database", len(pipes))
        build_pipes(pipes, current_timestep)
        self.logger.debug("Writing %s lines to database", len(lines))
        build_lines(lines, current_timestep)
        self.logger.debug('Writing %s gas stores to database', len(gas_stores))
        build_gas_stores(gas_stores, current_timestep)
        self.logger.debug('Writing %s gas terminals to database', len(gasterminal))
        build_gas_terminals(gasterminal, current_timestep)
        self.logger.debug('Building %s generators', len(generators))
        build_generator(generators, current_timestep)
        self.logger.debug('Building %s heattech interventions', len(heattech))
        build_heattech(heattech, current_timestep)

        self.logger.debug('Retiring %s generators', len(retirees))
        retire_generator(retirees)

    def get_model_inputs(self, data):
        # Get model inputs
        self.logger.debug("Energy Supply Wrapper received inputs in %s", data.current_timestep)

        fuel_prices = data.get_data("fuel_price")
        self.logger.debug('Input price: %s', fuel_prices)
        write_prices(fuel_prices, data.current_timestep)

        # inputs with just region
        param_name = 'EV_Cap'
        param_data = data.get_data(param_name)
        write_input_annual(param_data, param_name, data.current_timestep)

        inputs_with_region_and_interval = [
            # both modes
            'elecload',
            'gasload',
            'gasload_non_heat_res',
            'elecload_non_heat_res',
            'gasload_non_heat_com',
            'elecload_non_heat_com',
            'hydrogenload_non_heat_eh',
            # optimised mode only
            'heatload_res',
            'heatload_com',
            # constrained mode only
            'building_biomass_boiler',
            'building_elec_boiler',
            'building_heatpump',
            'building_gas_boiler',
            'building_hydrogen_boiler',
            'building_oil_boiler',
            'dh_biomass_boiler',
            'dh_elec_boiler',
            'dh_gas_CHP',
            'dh_hydrogen_fuelcell',
            #weather_data
            'wind_speed_eh',
            'wind_speed_bus',
            'insolation_eh',
            'insolation_bus',
            #transport
            'elec_trans',
        ]
        for input_ in inputs_with_region_and_interval:
            if input_ in self.inputs:
                self._load_input_2d(data, input_)

    def _load_input_2d(self, data_handle, name):
        data = data_handle.get_data(name)
        self.logger.debug("Input %s: %s", name, data)

        region_names, interval_names = self.get_dim_names(data.spec)

        self.logger.debug("Writing %s to database", name)
        write_input_timestep(
            data, name, data_handle.current_timestep, region_names, interval_names)

    def run_the_model(self):
        """Run the model
        """
        nismod_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        model_dir = os.path.normpath(os.path.join(nismod_dir, 'install', 'energy_supply'))
        model_path = os.path.join(model_dir, 'Energy_Supply_Master.mos')

        os.environ["ES_PATH"] = str(model_dir)
        self.logger.debug("\n\n***Running the Energy Supply Model***\n\n")
        self.logger.debug(check_output(['mosel', 'exec', model_path]))

    def retrieve_outputs(self, data, now):
        """Retrieves results from the model
        """
        # Open database connection
        conn = establish_connection()

        # Write timestep results to data handler
        for output in self.outputs:
            self.set_results(data, conn, output)

        # Close database connection
        conn.close()

        self.logger.debug("Energy supplyWrapper produced outputs in %s", now)

    def set_results(self, data_handle, conn, name):
        """Pass results from database to data handle
        """
        self.logger.info("Writing results for %s", name)
        spec = self.outputs[name]
        region_names, interval_names = self.get_dim_names(spec)

        output = get_timestep_output(
            conn, name, data_handle.current_timestep, region_names, interval_names)

        # set on smif DataHandle
        data_handle.set_results(name, output)

    def get_dim_names(self, spec):
        """Get region and interval names for a given input
        """
        dims = set(spec.dims)
        # HACK Assume two-dimensional, assume seasonal_week is the name for the intervals dim
        assert len(dims) == 2, "Expected 2 dimensions, got %s" % dims
        assert 'seasonal_week' in dims, "Expected 'seasonal_week' in dims, got %s" % dims
        dims.remove('seasonal_week')
        interval_dim = 'seasonal_week'
        region_dim = dims.pop()

        region_names = spec.dim_coords(region_dim).ids
        interval_names = spec.dim_coords(interval_dim).ids
        return region_names, interval_names


def establish_connection():
    """Connect to an existing database
    """
    config = ConfigParser()
    config.read(
        os.path.join(os.path.dirname(__file__), '..', '..', 'provision', 'dbconfig.ini'))
    dbconfig = config['energy-supply']
    conn = psycopg2.connect(**dbconfig)
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

    sql = """
    INSERT INTO "SimDuration" ("TimeStep", "Year", "Seasons", "Days", "Periods")
    VALUES (%s, %s, %s, %s, %s)
    """

    cur.execute(sql, ('1', year, '4', '7', '24'))

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def write_prices(data_array, year):
    """Write fuel price data

    Arguments
    ---------
    data : smif.DataArray
       Price data
    """
    # Open a cursor to perform database operations
    conn = establish_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM "FuelData" WHERE "Year"=%s;', (year, ))

    sql = """
        INSERT INTO "FuelData" ("Fuel_ID", "FuelType", "Year", "Season", "FuelCost")
        VALUES (%s, %s, %s, %s, %s)
        """

    dataframe = data_array.as_df().reset_index()

    # HACK hard code ids for fuel types - fix is to add a fuel types table that FuelData and
    # GeneratorParameters can both reference
    fuel_ids = {
        'gas': 1,
        'coal': 2,
        'nuclear': 3,
        'oil': 4,
        'biomass': 5,
        'electricity': 6
    }

    for datum in dataframe.itertuples():
        cur.execute(
            sql,
            (
                fuel_ids[datum.es_fuel_types],
                datum.es_fuel_types.capitalize(),
                year,
                datum.seasons,
                datum.fuel_price
            )
        )

    # Make the changes to the database persistent and close
    conn.commit()
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
            results = write_rows_into_array(
                region_interval_value_generator, regions, intervals)
        except(KeyError) as ex:
            raise KeyError(str(ex) + " in parameter %s" % output_parameter) from ex
    return results


def write_load_shed_costs(loadshedcost_elec, loadshedcost_gas, conn):
    """Write load shed cost parameters
    """
    with conn.cursor() as cur:
        cur.execute('DELETE FROM "LoadShedCosts";')
        cur.execute(
            'INSERT INTO "LoadShedCosts" ("EShedC", "GShedC") VALUES (%s, %s);',
            (loadshedcost_elec, loadshedcost_gas))


def write_flags(heat_mode,operation_mode,conn):
    """Write model configuration flags
    """
    with conn.cursor() as cur:
        cur.execute("DELETE FROM input_flags WHERE parameter = 'heat_mode';")
        cur.execute("DELETE FROM input_flags WHERE parameter = 'central_decentral_mode';")

        cur.execute(
            'INSERT INTO input_flags (parameter, value) VALUES (%s, %s);',
            ('heat_mode', heat_mode))
        cur.execute(
            'INSERT INTO input_flags (parameter, value) VALUES (%s, %s);',
            ('central_decentral_mode', operation_mode))


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


def build_generator(plants, current_timestep):
    """Writes an intervention into the GeneratorData table

    Arguments
    ---------
    plants : list
    """
    conn = establish_connection()
    cur = conn.cursor()

    expected_keys = ['type', 'name', 'location', 'min_power', 'capacity',
                     'build_year', 'technical_lifetime', 'sys_layer']

    for plant in plants:

        missing = []
        valid = True
        for key in expected_keys:
            if key not in plant.keys():
                missing.append(key)
                valid = False

        if not valid:
            raise ValueError("Keys {} missing for {}".format(
                             missing,
                             plant['name'])
            )
        try:
            plant['type'] = int(plant['type'])
        except TypeError:
            pass

        if isinstance(plant['type'], str):
            plant_type = {'ccgt': 1,
                          'coal': 2,
                          'nuclear': 4,
                          'hydro': 5,
                          'oil': 6,
                          'ocgt (flexible generation)': 7,
                          'biomass': 10,
                          'interconnector': 11,
                          'chp gas': 13,
                          'pumped_storage': 15,
                          'gas fired generation of ehs': 20,
                          'efw chp of ehs ': 21,
                          'biomass chp of ehs ': 22,
                          'h2 fuel cell ': 30,
                          'wind onshore' : 3,
                          'wind offshore': 12,
                          'pv'         : 23 ,
                          'dummygenerator': 100}[plant['type'].lower()]
        elif isinstance(plant['type'], int):
            plant_type = plant['type']
        else:
            raise ValueError("'type' field '{}' is incorrect".format(
                plant['type']))

        def extract_value(generator, field_name):
            if isinstance(generator[field_name], dict):
                value = float(generator[field_name]['value'])
            else:
                value = float(generator[field_name])
            return value

        min_power = extract_value(plant, 'min_power')
        capacity = extract_value(plant, 'capacity')
        lifetime = extract_value(plant, 'technical_lifetime')

        if int(plant['sys_layer']) == 2:

            sql = """
            INSERT INTO "GeneratorData" ("Type", "GeneratorName", "EH_Conn_Num","MinPower",
                "MaxPower", "Year", "Retire", "SysLayer")
            VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)"""
            data = (plant_type,
                    plant['name'],
                    plant['location'],
                    min_power,
                    capacity,
                    current_timestep,
                    float(plant['build_year']) + lifetime,
                    plant['sys_layer']
                    )

        elif plant_type == 1:

            sql = """
                INSERT INTO "GeneratorData" ("Type", "GeneratorName", "GasNode", "BusNum",
                    "MinPower", "MaxPower", "Year", "Retire", "SysLayer")
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
            data = (plant_type,
                    plant['name'],
                    plant['to_location'],
                    plant['location'],
                    min_power,
                    capacity,
                    current_timestep,
                    float(plant['build_year']) + lifetime,
                    plant['sys_layer']
                    )

        else:

            sql = """
            INSERT INTO "GeneratorData" ("Type", "GeneratorName",  "BusNum", "MinPower",
                "MaxPower", "Year", "Retire", "SysLayer")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            data = (plant_type,
                    plant['name'],
                    plant['location'],
                    min_power,
                    capacity,
                    current_timestep,
                    float(plant['build_year']) + lifetime,
                    plant['sys_layer']
                    )
        try:
            cur.execute(sql, data)
        except psycopg2.DataError as ex:
            print(sql, data)
            raise psycopg2.DataError(ex)
        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def get_distributed_eh(location, year):

    sql =  """
    SELECT "OnshoreWindCap", "OffshoreWindCap", "PvCapacity"
    FROM "WindPVData_EH"
    WHERE "EH_Conn_Num"=%s AND "Year"=%s;
    """

    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute(sql, (location, year))
        mapping = cur.fetchone()
    conn.close()
    return mapping


def get_distributed_tran(location, year):

    sql =  """
    SELECT "OnshoreWindCap", "OffshoreWindCap", "PvCapacity"
    FROM "WindPVData_Tran"
    WHERE "BusNum"=%s AND "Year"=%s;
    """

    conn = establish_connection()
    # Open a cursor to perform database operations
    with conn.cursor() as cur:
        cur.execute(sql, (location, year))
        mapping = cur.fetchone()
    conn.close()
    return mapping


def build_distributed(plants, current_timestep):
    """Write a list of interventions into the WindPVData_* table

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
            plant_remap[location]['build_year'] = current_timestep
            plant_remap[location]['table_name'] = plant['table_name']
            if  plant['type'] == 'offshorewind':
                plant_remap[location]['offshore'] += float(plant['capacity']['value'])
            elif plant['type'] == 'onshorewind':
                plant_remap[location]['onshore'] += float(plant['capacity']['value'])
            elif plant['type'] == 'pv':
                plant_remap[location]['pv'] += float(plant['capacity']['value'])
            else:
                raise ValueError("Cannot read type of {}".format(plant))

    for index, (location, plant) in enumerate(plant_remap.items()):

        if plant['table_name'] == 'WindPVData_EH':
            sql = """
            INSERT INTO "WindPVData_EH" ("EH_Conn_Num", "Year", "OnshoreWindCap",
                "OffshoreWindCap", "PvCapacity")
            VALUES (%s, %s, %s, %s, %s)
            """

        elif plant['table_name'] == 'WindPVData_Tran':
            sql = """
            INSERT INTO "WindPVData_Tran" ("BusNum", "Year", "OnshoreWindCap",
                "OffshoreWindCap","PvCapacity")
            VALUES (%s, %s, %s, %s, %s)
            """
        else:
            raise ValueError("Cannot read table name of element {}: {}".format(index, plant))

        data = (
                location,
                current_timestep,
                plant['onshore'],
                plant['offshore'],
                plant['pv'])

        # print("Updating location {} into table {}".format(location, plant['table_name']))

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


def build_gas_stores(gas_stores, current_timestep):
    """Set up the initial system from a list of interventions

    Write in the all interventions with the intervention_name ``gasstore``
    to the GasStore table.

    Arguments
    ---------
    gas_stores : list

    Notes
    -----
    GasStorage" (
        StorageNum integer,
        region integer,
        Name character varying(255),
        Year double precision,
        InFlowCap double precision,
        OutFlowCap double precision,
        StorageCap double precision,
        OutFlowCost double precision
        Syslayer integer
    """
    conn = establish_connection()
    cur = conn.cursor()

    cur.execute("""DELETE FROM "GasStorage";""")

    for store_num, store in enumerate(gas_stores):

        sql = """
        INSERT INTO "GasStorage" ("StorageNum", "region", "Name", "Year", "InFlowCap",
            "OutFlowCap", "StorageCap", "OutFlowCost", "Syslayer")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (store_num + 1,
                store['location'],
                store['name'],
                current_timestep,
                store['inflowcap'],
                store['outflowcap'],
                store['capacity']['value'],
                store['outflowcost'],
                store['syslayer']
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def build_gas_terminals(gas_terminals, current_timestep):
    """Set up the initial system from a list of interventions

    Write in the all interventions to the GasTerminal table.

    Arguments
    ---------
    gas_terminals : list

    Notes
    -----
          Column       |          Type          |
    -------------------+------------------------+
    TerminalNum        | integer                |
    Year               | integer                |
    Name               | character varying(255) |
    GasNode            | integer                |
    GasTerminalOptCost | double precision       |
    TerminalCapacity   | double precision       |
    LNGCapacity        | double precision       |
    InterCapacity      | double precision       |
    DomCapacity        | double precision       |

    """
    conn = establish_connection()
    cur = conn.cursor()

    cur.execute("""DELETE FROM "GasTerminal";""")

    for terminal_num, terminal in enumerate(gas_terminals):

        sql = """
        INSERT INTO "GasTerminal" ("TerminalNum", "Year", "Name", "GasNode",
            "GasTerminalOptCost", "TerminalCapacity", "LNGCapacity", "InterCapacity",
            "DomCapacity")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (terminal_num + 1,
                current_timestep,
                terminal['name'],
                terminal['location'],
                terminal['operational_cost']['value'],
                terminal['capacity']['value'],
                terminal['lngcapacity'],
                terminal['intercapacity'],
                terminal['domcapacity']
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def build_pipes(pipes, current_timestep):
    """Set up the initial system from a list of interventions

    Write in the all pipes to the PipeData table.

    Arguments
    ---------
    pipes : list
    current_timestep : int

    Notes
    -----
    Column  |       Type       |
    --------+------------------+
    PipeNum | integer          |
    FromNode| integer          |
    ToNode  | integer          |
    Year    | integer          |
    Length  | double precision |
    Diameter| double precision |
    PipeEff | double precision |
    MinFlow | double precision |
    MaxFlow | double precision |

    """
    conn = establish_connection()
    cur = conn.cursor()

    for pipe_num, pipe in enumerate(pipes):

        sql = """
        INSERT INTO "PipeData" ("PipeNum", "FromNode", "ToNode", "Year", "Length", "Diameter",
            "PipeEff", "MinFlow", "MaxFlow")
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data = (pipe_num + 1,
                pipe['location'],
                pipe['to_location'],
                current_timestep,
                pipe['length']['value'],
                pipe['diameter']['value'],
                pipe['pipeeff'],
                pipe['minflow'],
                pipe['maxflow']
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def build_heattech(heat_techs, current_timestep):
    """Set up system from list of interventions

    Write lines into the HeatTechData table

    Arguments
    ---------
    heat_techs : list
    current_timestep : int

    Notes
    -----
       Column    |         Type          |
    -------------+-----------------------+
    HeatNum      | integer               |
    Type         | integer               |
    HeatTechName | character varying(50) |
    EH_Conn_Num  | integer               |
    MinPower     | double precision      |
    MaxPower     | double precision      |
    Year         | integer               |
    """
    conn = establish_connection()
    cur = conn.cursor()

    for heat_num, heat_tech in enumerate(heat_techs):

        sql = """
        INSERT INTO "HeatTechData" ("HeatNum", "Type", "HeatTechName", "EH_Conn_Num",
            "MinPower", "MaxPower", "Year")
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        data = (heat_num + 1,
                heat_tech['type'],
                heat_tech['name'],
                heat_tech['location'],
                heat_tech['minpower'],
                heat_tech['capacity']['value'],
                current_timestep
                )

        cur.execute(sql, data)

        # Make the changes to the database persistent
        conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def build_lines(lines, current_timestep):
    """Set up the initial system from a list of interventions

    Write in the all lines to the LineData table.

    Arguments
    ---------
    lines : list
    current_timestep : int

    Notes
    -----

    Column     |       Type       |
    -----------+------------------+
    LineNum    | integer          |
    FromBus    | integer          |
    ToBus      | integer          |
    Year       | integer          |
    MaxCapacity| double precision |


    """
    conn = establish_connection()
    cur = conn.cursor()

    for line_num, line in enumerate(lines):

        sql = """
        INSERT INTO "LineData" ("LineNum", "FromBus", "ToBus", "Year", "MaxCapacity")
        VALUES (%s, %s, %s, %s, %s)
        """

        data = (line_num + 1,
                line['location'],
                line['to_location'],
                current_timestep,
                line['capacity']['value']
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


def write_input_timestep(input_data, parameter_name, year, region_names, interval_names):
    """Writes input data into database table

    Uses the index of the numpy array as a reference to interval and region definitions

    Arguments
    ---------
    input_data : smif.data_layer.data_array.DataArray
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

    cur.execute(
        'DELETE FROM "input_timestep" WHERE parameter=%s AND year=%s;',
        (parameter_name, year))

    sql = """
        INSERT INTO
        input_timestep (year, season, day, period, region_id, parameter, value)
        VALUES %s
        """

    region_mapping = get_region_mapping(parameter_name)

    def values(input_data):
        """Generate values tuples from input data
        """
        it = np.nditer(input_data.as_ndarray(), flags=['multi_index'])
        while not it.finished:
            cell = it[0]

            region, interval = it.multi_index
            season, day, period = parse_season_day_period(int(interval_names[interval]))
            try:
                region_id = region_mapping[int(region_names[region])]
            except KeyError as ex:
                msg = "Error when trying to write '{}'. Regions: {}"
                print(msg.format(parameter_name, region_mapping))
                raise ex

            yield (year, season, day, period, region_id, parameter_name, float(cell))
            it.iternext()

    # bulk insert of `page_size` records at a time, runs faster than one-row-at-a-time
    template = "(%s, %s, %s, %s, %s, %s, %s)"
    psycopg2.extras.execute_values(cur, sql, values(input_data), template, page_size=1000)

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()


def write_input_annual(data, parameter_name, timestep):
    assert len(data.dims) == 1, "Expected a single dimension for %s, got %s" % (
        parameter_name, data.dims)
    region_dim_name = data.dims[0]

    conn = establish_connection()
    with conn.cursor() as cur:
        cur.execute(
            'DELETE FROM input_annual WHERE parameter=%s AND year=%s;',
            (parameter_name, timestep)
        )
        sql = """INSERT INTO
            input_annual (year, region_id, parameter, value)
            VALUES (%s, %s, %s, %s)
            """
        for (region_id, ), value in data.as_df().itertuples():
            cur.execute(
                sql,
                (timestep, region_id, parameter_name, value)
            )
    conn.commit()
    conn.close()
