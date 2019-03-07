"""Download from NISMOD-DB-API

Add a config block to dbconfig.ini like::

        [nismod-api]
        user=username
        password=longsecurerandompassword

Or set NISMOD_API_USER and NISMOD_API_PASSWORD environment variables

"""
import configparser
import csv
import json
import os
import shutil

import pandas
import requests

from smif.data_layer.file import CSVDataStore, ParquetDataStore
from smif.data_layer.data_array import DataArray
from smif.metadata import Spec


CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')
STORE_BASE_PATH = os.path.join(os.path.dirname(__file__), '..')
PERSISTENT_DATA_PATH = os.path.join(os.path.dirname(__file__), 'persistent_data')
POPULATION_MIN_YEAR = 2011
POPULATION_MAX_YEAR = 2020
POPULATION_DATA_VERSION = 5


def main():
    # Read connection details
    if 'NISMOD_API_USER' in os.environ and 'NISMOD_API_PASSWORD' in os.environ:
        username = os.environ['NISMOD_API_USER']
        password = os.environ['NISMOD_API_PASSWORD']
    else:
        parser = configparser.ConfigParser()
        parser.read(os.path.join(os.path.dirname(__file__), 'dbconfig.ini'))
        username = parser['nismod-api']['user']
        password = parser['nismod-api']['password']

    auth = (username, password)

    try:
        os.mkdir(CACHE_PATH)
    except FileExistsError:
        pass

    # Population
    get_population(auth)
    process_oa_population()
    process_oa_to_lad_population()

    # Read
    oa_pop = pandas.read_csv(os.path.join(CACHE_PATH, 'oa_population.csv'))
    lad_pop = pandas.read_csv(os.path.join(CACHE_PATH, 'lad_population.csv'))

    # to DataArray
    years = list(range(POPULATION_MIN_YEAR, POPULATION_MAX_YEAR + 1))
    oas = list(oa_pop.oa.unique())
    oa_spec = Spec(
        name='population',
        dims=['timestep', 'oa'],
        coords={'oa': oas, 'timestep': years},
        dtype='int'
    )

    lads = list(lad_pop.lad16cd.unique())
    lad_spec = Spec(
        name='population',
        dims=['timestep', 'lad16cd'],
        coords={'lad16cd': lads, 'timestep': years},
        dtype='int'
    )

    # Write to CSV and Parquet stores
    text_store = CSVDataStore(STORE_BASE_PATH)
    binary_store = ParquetDataStore(STORE_BASE_PATH)

    lad_key = 'population_nismod_db.v5_lad16'
    lad_pop_da = DataArray.from_df(lad_spec, lad_pop.set_index(lad_spec.dims))
    text_store.write_scenario_variant_data('{}.csv'.format(lad_key), lad_pop_da)
    binary_store.write_scenario_variant_data('{}.parquet'.format(lad_key), lad_pop_da)

    oa_key = 'population_nismod_db.v5_oa'
    oa_pop_da = DataArray.from_df(oa_spec, oa_pop.set_index(oa_spec.dims))
    text_store.write_scenario_variant_data('{}.csv'.format(oa_key), oa_pop_da)
    binary_store.write_scenario_variant_data('{}.parquet'.format(oa_key), oa_pop_da)

def get_population(auth):
    pop_url = 'https://www.nismod.ac.uk/api/data/households/population_totals'
    for year in range(POPULATION_MIN_YEAR, POPULATION_MAX_YEAR + 1):
        oa_pop_file = get_oa_population_file(year)
        if not os.path.exists(oa_pop_file):
            print("Get oa population", year)
            r = requests.get(
                pop_url,
                auth=auth,
                params={
                    'scale': 'oa',
                    'year': year,
                    'data_version': POPULATION_DATA_VERSION
                },
                stream=True
            )
            with open(oa_pop_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)


def get_oa_population_file(year):
    return os.path.join(CACHE_PATH, 'oa_population_{}.json'.format(year))


def process_oa_population():
    oa_csv_path = os.path.join(CACHE_PATH, 'oa_population.csv')
    with open(oa_csv_path, 'w', newline='') as oa_fh:
        oa_writer = csv.DictWriter(
            oa_fh,
            fieldnames=('oa', 'population', 'timestep')
        )
        oa_writer.writeheader()
        for year in range(POPULATION_MIN_YEAR, POPULATION_MAX_YEAR + 1):
            print("Process oa population", year)
            with open(get_oa_population_file(year), 'r') as year_fh:
                data = json.load(year_fh)
                oa_writer.writerows({
                    'oa': d['oa'],
                    'population': int(d['total_population']),
                    'timestep': int(d['year'])
                } for d in data)


def process_oa_to_lad_population():
    # read in lookups
    oa_to_lad = pandas.read_csv(
        os.path.join(PERSISTENT_DATA_PATH, 'gb_geog_lookup.csv.gz'), compression='infer')
    lad_to_lad = pandas.read_csv(os.path.join(PERSISTENT_DATA_PATH, 'lad_nmcd_changes.csv'))

    # read in OA population
    oa_pop = pandas.read_csv(os.path.join(CACHE_PATH, 'oa_population.csv'))

    # merge OA population with lookup, aggregate to LAD
    lad11_pop = oa_pop.merge(
        oa_to_lad, left_on='oa', right_on='OA'
    )[
        ['oa', 'population', 'timestep', 'LAD']
    ].groupby(
        ['timestep', 'LAD']
    ).sum().reset_index()

    # merge LAD11 population with changed codes lookup, output with LAD16 codes
    lad16_pop = lad11_pop.merge(
        lad_to_lad[['lad11cd', 'lad16cd']], left_on='LAD', right_on='lad11cd'
    )[
        ['timestep', 'lad16cd', 'population']
    ]
    lad16_pop.to_csv(os.path.join(CACHE_PATH, 'lad_population.csv'), index=False)


if __name__ == '__main__':
    main()
