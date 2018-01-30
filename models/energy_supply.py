from smif.model.sector_model import SectorModel
from subprocess import check_output
import os
import psycopg2
from collections import namedtuple

class EnergySupplyWrapper(SectorModel):
    """Wraps the energy supply model
    """
    @staticmethod
    def establish_connection():
        """Connect to an existing database

        """
        conn = psycopg2.connect("dbname=vagrant user=vagrant")
        return conn

    def parse_season_period(self, season_period_string):
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

    @staticmethod
    def _get_day(period):
        """Returns the day of the week

        """
        day = ((period - 1) // 24) + 1
        return day

    def _get_node_numbers(self):
        """Returns the number of the bus associated with the region
        """
        conn = self.establish_connection()

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

    def _get_bus_numbers(self):
        """Returns the number of the bus associated with the region
        """
        conn = self.establish_connection()

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

    def write_gas_demand_data(self, data):
        """Writes gas demand data into the database table

        Columns: year, season, day, period (hour), bus number, value

        Arguments
        ---------
        data : list
            A dict of list of SpaceTimeValue tuples
        """
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        cur = conn.cursor()

        node_numbers = self._get_node_numbers()

        gas_data = data['gas_demand']
        print("Inserting {} rows of data".format(len(gas_data)))

        sql = """INSERT INTO "GasLoad" (Year, Season, Day, Period, GasNode, GasLoad) VALUES (%s, %s, %s, %s, %s, %s)"""
        for row in gas_data:
            season, period = self.parse_season_period(row.interval)
            day = self._get_day(period)
            node_number = int(node_numbers[row.region])
            insert_data = (data['timestep'],
                           season,
                           day,
                           period,
                           node_number,
                           row.value)
            # print("Inserting {} into GasLoad".format(insert_data))
            cur.execute(sql, insert_data)

        # Make the changes to the database persistent
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()


    def write_electricity_demand_data(self, data):
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
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        cur = conn.cursor()

        bus_numbers = self._get_bus_numbers()

        elec_data = data['electricity_demand']
        print("Inserting {} rows of data".format(len(elec_data)))

        sql = """INSERT INTO "ElecLoad" (Year, Season, Day, Period, BusNumber, ElecLoad) VALUES (%s, %s, %s, %s, %s, %s)"""
        for row in elec_data:
            season, period = self.parse_season_period(row.interval)
            day = self._get_day(period)
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

    def get_cooling_water_demand(self):
        """Calculated cooling water demand as a function of thermal power station operation

        Returns
        -------
        list
            A list of dicts of water demand, with season, period, value
        """
        # Connect to an existing database
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        with conn.cursor() as cur:

            sql = """SELECT season, period, thermal from "O_Elec_Mix";"""
            cur.execute(sql)

            water_demand = []
            for row in cur.fetchall():
                cooling_water = self._calculate_water_demand(row[2])
                water_demand.append({'id': "{}_{}".format(row[0], row[1]),
                                     'water_demand': cooling_water})

        return water_demand

    def get_total_emissions(self):
        """Gets total emissions from the output table

        Returns
        -------
        emissions : float
            Annual emissions in tCO2
        """
        # Connect to an existing database
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            sql = """SELECT total_emissions from "O_Emissions";"""
            cur.execute(sql)
            emissions = cur.fetchone()[0]
        return emissions

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

    def get_total_cost(self):
        """Gets total cost from the objective function table

        Returns
        -------
        total_cost : float
            The total cost in GBP
        """
        # Connect to an existing database
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            sql = """SELECT objective from "O_Objective";"""
            cur.execute(sql)
            total_cost = cur.fetchone()[0]
        return total_cost

    def get_prices(self):
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

        conn = self.establish_connection()
        # Open a cursor to perform database operations
        with conn.cursor() as cur:
            sql = """SELECT season, period, e_prices from "O_Elec_Prices";"""
            cur.execute(sql)

            for row in cur.fetchall():
                electricity_prices.append({'id': "{}_{}".format(row[0], row[1]),
                                           'electricity_price': row[2]})

        return electricity_prices

    def get_results(self):
        """Gets the results as defined in ``outputs.yaml``
        """
        return {'water_demand': self.get_cooling_water_demand(),
                'total_cost': self.get_total_cost(),
                'total_emissions': self.get_total_emissions(),
                'electricity_prices': self.get_prices()}

    def get_model_executable(self):
        """Return path of current python interpreter
        """
        executable = '/vagrant/models/energy_supply/model/MISTRAL_ES.exe'

        return os.path.join(executable)

    def build_power_station(self, name, plant_type, region, capacity, build_year,
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
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        cur = conn.cursor()

        bus_num = self._get_bus_numbers()

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

    def increase_gas_terminal_capacity(self, terminal_number, capacity_increase):
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
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        cur = conn.cursor()

        node_num = self._get_node_numbers()

        sql = """UPDATE "GasTerminal" SET terminalcapacity=terminalcapacity+(%s) \
                 WHERE terminalnumber = (%s)"""

        query_data = (capacity_increase, terminal_number)

        cur.execute(sql, query_data)

        # Make the changes to the database persistent
        conn.commit()

        # Close communication with the database
        cur.close()
        conn.close()

    def initialise(self, initial_conditions):
        """Set up the initial system from a list of interventions

        Arguments
        ---------
        initial_conditions : list
        """
        pass

    def simulate(self, decisions, state, data):
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
                self.build_power_station(name, plant_type, region, capacity,
                                         build_year,
                                         operational_life)
            elif decision.name == 'IOG_gas_terminal_expansion':
                capacity = decision.data['capacity']['value']
                terminal_number = decision.data['gas_terminal_number']['value']
                self.increase_gas_terminal_capacity(terminal_number, capacity)

        # Write demand data into input tables
        # print(data)
        conn = self.establish_connection()
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("""DELETE FROM "ElecLoad";""")
        cur.execute("""DELETE FROM "GasLoad";""")
        # Make the changes to the database persistent
        conn.commit()
        # Close communication with the database
        cur.close()
        conn.close()

        self.write_electricity_demand_data(data)
        self.write_gas_demand_data(data)

        # Run the model
        arguments = [self.get_model_executable()]
        output = check_output(arguments)

        results = self.get_results()
        print("Emissions: {}".format(results['total_emissions']))
        print("Total Cost: {}".format(results['total_cost']))
        return results

    def extract_obj(self, results):
        return results

def main():
    SpaceTimeValue = namedtuple('SpaceTimeValue', ['region', 'interval', 'value', 'units'])

    electricity_demand = [SpaceTimeValue('Scotland', ('1_1'), 2.48, 'GW'),
                          SpaceTimeValue('Wales', ('1_1'), 2.48, 'GW'),
                          SpaceTimeValue('England', ('1_1'), 2.48, 'GW')]
    gas_demand = [SpaceTimeValue('Scotland', ('1_1'), 2.48, 'GW'),
                  SpaceTimeValue('Wales', ('1_1'), 2.48, 'GW'),
                  SpaceTimeValue('England', ('1_1'), 2.48, 'GW')]

    data = {'timestep': 2015,
            'electricity_demand': electricity_demand,
            'gas_demand': gas_demand}

    decision = [{'capacity': {'units': 'MW', 'value': 1000},
                 'capital_cost': {'units': '£(million)/MW', 'value': 3.5},
                 'economic_lifetime': {'units': 'years', 'value': 30},
                 'operational_year': {'units': 'year', 'value': 2030},
                 'name': 'nuclear_power_station',
                 'location': {'units': 'string', 'value': 'England'},
                 'power_generation_type': {'units': 'number', 'value': 4},
                 'operational_life': {'units': 'years', 'value': 40}},
                {'name': 'IOG_gas_terminal_expansion',
                 'operational_life': {'units': 'years', 'value': 30},
                 'gas_terminal_number': {'units': 'number', 'value': 8},
                 'operational_year': {'units': 'year', 'value': 2020},
                 'capacity': {'units': 'mcm', 'value': 10},
                 'economic_lifetime': {'units': 'years', 'value': 25},
                 'location': {'units': 'string', 'value': 'England'},
                 'capital_cost': {'units': '£(million)/mcm', 'value': 10}}]

    energy = EnergySupplyWrapper('energy_supply')
    print("Running model")
    energy.simulate(decision, [], data)
    print("Finished running model")

    results = energy.get_results()

    print("Emissions: {}".format(results['total_emissions']))
    print("Total Cost: {}".format(results['total_cost']))


if __name__ == '__main__':
    main()
