"""Generate a yaml file containing valid time_interval definitions

Transport
---------

The transport simulation model models a single average day.  This single day
is then mapped to the 365 days in the year.

- name: "1"
  represents: [
        ["P0D", "P1D"],
        ["P1D", "P2D"]
               ]
  ...

Digital Communications
----------------------

The digital communications model doesn't have an internal time-interval, and
models the entire year of operation of the communications network.

- name: "1"
  represents: [["P0D", "P365D"]]

Energy Supply
-------------

The energy supply model has four seasons, corresponding to the following
months::

1) Dec/Jan/Feb - week 43 - 3 - hours 7224 - 8759; 0 - 671;
2) Mar/Apr/May - week 4 - 16 - hours 672 - 2855
3) Jun/Jul/Aug - week 17 - 29 - hours 2856 - 5039
4) Sep/Oct/Nov - week 30 - 42 - 5040 - 7223

168 periods (hours) are defined which represent one week per season.

For example, Period 1, Season 1, is midnight to 1am on the 1st December.
Period 168, Season 1 is 23:00 to 00:00, 6 days later, on the 6th December.
Period 1, Season 1, also corresonds to midnight to 1am on the 7th, 14th,
21st, 28th... December.

The internal representation of simulation time in `smif` is of hours,
with midnight to 1am on the 1st Jan, hour 0, and 23:00 to midnight on 31st December, hour 8759.

The problem is to map repeating intervals onto the year.

- name: 1,
  represents: [[PT0H,PT1H], [PT168H, PT169H]...]

There are 52 weeks in the year. 52 weeks of 4 seasons of 13 weeks each.
Each week contains 168 hours.

"""

from datetime import date, timedelta, datetime
from calendar import monthrange
from yaml import load, dump
from itertools import cycle
import pytest
from collections import OrderedDict

def make_energy_supply():
    """Maps each of hours in the 52 weeks of the year to the 168 hours of a 
    representative week in each of the four seasons

    1) Dec/Jan/Feb - week 43 - 3 - hours 7224 - 8759; 0 - 671;
    2) Mar/Apr/May - week 4 - 16 - hours 672 - 2855
    3) Jun/Jul/Aug - week 17 - 29 - hours 2856 - 5039
    4) Sep/Oct/Nov - week 30 - 42 - 5040 - 7223


    Season,Start,End
    winter,PT0H,PT167H
    spring,PT2160H,PT2327H
    summer,PT4344H,PT4511H
    autumn,PT6552H,PT6719H

    """
    results = OrderedDict()

    winter = list(range(0, 672))
    winter.extend(list(range(7224, 8760)))
    spring = list(range(672, 2856))
    summer = list(range(2856, 5040))
    autumn = list(range(5040, 7224))

    season_hours = {1: winter,
                    2: spring,
                    3: summer,
                    4: autumn}
    for season, hours in season_hours.items():
        for (smif_hour, es_hour) in zip(hours, cycle(range(168))):

            hour_id = (168 * (season - 1)) + es_hour + 1

            if str(hour_id) in results.keys():
                results[str(hour_id)].append(["PT{}H".format(smif_hour), "PT{}H".format(smif_hour + 1)])
            else:
                results[str(hour_id)] = [["PT{}H".format(smif_hour), "PT{}H".format(smif_hour + 1)]]

        new_results = []
        for name, represents in results.items():
            new_results.append({'name': name, 'represents': represents})

    return new_results

def make_season_ranges():
    pass


def get_season_of_hour(hour):

    seasons = {1: [12, 1, 2],
               2: [3, 4, 5],
               3: [6, 7, 8],
               4: [8, 9, 10]}

    season_range = {}

    for season, months in seasons.items():
        month_range = []
        for month in months:
            print(number_days_in(month))
            month_range.append(first_day_of_month(month))
        season_range[season] = month_range

        print(month_range[0], hour, month_range[2])
        if hour >= month_range[0] and hour <= month_range[2]:
            return season
        else:
            pass
    return season


def make_hourly():

    results = []

    for hour in range(8760):

        name = hour + 1
        start_code = "PT{}H".format(int(hour))
        end_hour = hour + 1
        end_code = "PT{}H".format(int(end_hour))
        results.append({'name': name,
                        'represents': [[start_code, end_code]]})

    return results


def make_dict():
    """

    Parameters
    ----------
    data : list
        A list containing a dictionary of header/values
    func : :py:func
        A python function which operates upon the data
    arguments : tuple
        A tuple of header names corresponding to `func` arguments


    """
    seasons = {1: [1]}#12, 2],
            #    2: [3, 4, 5],
            #    3: [6, 7, 8],
            #    4: [8, 9, 10]}
    results = []
    for season, months in seasons.items():
        for month in months:
            first_hour_of_month = first_day_of_month(month)
            # Step over days in month, repeating 168 hours until days run out
            for days in range(1, number_days_in(month)):
                if (days == 1) or (days - 1 % 7 == 0):
                    first_hour_of_week = (days - 1) * 24
                    for hour in range(1, 169):
                        if hour / 24 <= number_days_in(month):
                            name = "{}_{}".format(int(season), int(hour))
                            start_hour = first_hour_of_week + first_hour_of_month + hour
                            start_code = "P{}H".format(int(start_hour - 1))
                            end_hour = start_hour
                            end_code = "P{}H".format(int(end_hour))
                            print(name, start_code, end_code)
                            results.append({'id': name,
                                            'start': start_code,
                                            'end': end_code})
    return results


def first_day_of_month(month):
    """Returns the first day of the month in terms of the hour index

    Arguments
    ---------
    month : int
        The index of the month, 'Jan' = 1; 'Dec' = 12

    Returns
    -------
    hour_index : int
    """
    start_year = 2017
    start_month = 1
    start_day = 1
    start_hour = 0

    beginning_of_year = datetime(start_year,
                                 start_month,
                                 start_day,
                                 start_hour)

    first_day = datetime(start_year,
                         month,
                         start_day,
                         start_hour)

    delta = first_day - beginning_of_year

    SECONDS_PER_MINUTE = 60
    MINUTES_PER_HOUR = 60

    return delta.total_seconds() / (SECONDS_PER_MINUTE * MINUTES_PER_HOUR)

def number_days_in(month):
    """Find number of days in a month
    """
    return monthrange(2017, month)[1]


def create_water_supply_periods():
    results = []
    for day in range(365):
        name = str(day + 1)
        start_code = "P{}D".format(day)
        end_code = "P{}D".format(day + 1)
        results.append({'id': name,
                        'start': start_code,
                        'end': end_code})
    return results    


def create_transport_periods():
    results = []
    for day in range(365):
        name = "1"
        start_code = "P{}D".format(day)
        end_code = "P{}D".format(day + 1)
        results.append({'id': name,
                        'start': start_code,
                        'end': end_code})
    return results

from csv import DictWriter

def write_yaml_file(interval_data, filename):
    """Writes the period configuration structure into a yaml file

    Parameters
    ----------
    interval_data: list
        A list of period dicts
    filename: str
        The name of the file to produce
    """
    with open(filename, 'w+') as yamlfile:
        dump(interval_data, yamlfile, default_flow_style=False)


def write_csv_file(interval_data, filename):
    """Writes the period configuration structure into a csv file

    Parameters
    ----------
    interval_data: list
        A list of period dicts
    filename: str
        The name of the file to produce
    """
    with open(filename, 'w+') as csvfile:
        headers = ['name', 'represents']
        writer = DictWriter(csvfile, headers)
        writer.writeheader()
        writer.writerows(interval_data)

if __name__ == '__main__':

    # interval_data = create_transport_periods()
    # write_file(interval_data, './test/model_configurations/transport_minimal/time_intervals.csv')

    # interval_data = create_water_supply_periods()
    # write_file(interval_data, './test/model_configurations/water_supply_minimal/time_intervals.csv')    

    interval_data = make_energy_supply()
    write_csv_file(interval_data, '../data/dimensions/seasonal_week.csv')

    interval_data = make_hourly()
    write_csv_file(interval_data, '../data/dimensions/hourly_intervals.csv')

class TestEnergySupplyIntervals:

    def test_intervals(self):

        actual = make_energy_supply()
        print(actual[0])
        assert actual[0]['name'] == '1'
        actual_intervals = actual[0]['represents']
        assert isinstance(actual_intervals, list)
        assert actual_intervals[0] == ['PT0H', 'PT1H']
        assert actual[167]['represents'][0] == ['PT167H', 'PT168H']
        assert len(actual[167]['represents']) == 13
        assert len(actual) == 672

        expected = [['PT0H', 'PT1H'], ['PT168H', 'PT169H'], ['PT336H', 'PT337H'], ['PT504H', 'PT505H'], ['PT7224H', 'PT7225H'], ['PT7392H', 'PT7393H'], ['PT7560H', 'PT7561H'], ['PT7728H', 'PT7729H'], ['PT7896H', 'PT7897H'], ['PT8064H', 'PT8065H'], ['PT8232H', 'PT8233H'], ['PT8400H', 'PT8401H'], ['PT8568H', 'PT8569H'], ['PT8736H', 'PT8737H']]

        assert (actual_intervals) == (expected)

