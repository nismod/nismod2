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
import sys

from requests_threads import AsyncSession


CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')
BUILDINGS_YEAR = 2017
POPULATION_MIN_YEAR = 2011
POPULATION_MAX_YEAR = 2020
POPULATION_DATA_VERSION = 5


# Override default to be large, in case of LARGE geometries in csv fields
FIELD_SIZE_LIMIT = sys.maxsize
while True:
    try:
        csv.field_size_limit(FIELD_SIZE_LIMIT)
        break
    except OverflowError:
        FIELD_SIZE_LIMIT = int(FIELD_SIZE_LIMIT/2)


async def main():
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

    # LAD 2011, Census-Merged
    await get_lads(auth)
    lads = load_lads()
    # OA 2011
    await get_oas(auth, lads)
    process_geographies(lads)

    # Population
    await get_population(auth)
    process_oa_population()

    # Buildings
    await get_buildings(auth)


async def get_buildings(auth):
    oas_csv_path = os.path.join(CACHE_PATH, 'oas.csv')
    with open(oas_csv_path, 'r') as oas_fh:
        oas_r = csv.DictReader(oas_fh)
        for oa in oas_r:
            print("Get buildings for", oa['oa_code'])
            oa_file = os.path.join(
                CACHE_PATH, oa['lad_code'], 'buildings_{}.json'.format(oa['oa_code']))

            try:
                os.mkdir(os.path.join(CACHE_PATH, oa['lad_code']))
            except FileExistsError:
                pass

            if not os.path.exists(oa_file):
                r = await session.get(
                    'https://www.nismod.ac.uk/api/data/mastermap/buildings',
                    auth=auth,
                    params={
                        'scale': 'oa',
                        'area_codes': oa['oa_code'],
                        'building_year': BUILDINGS_YEAR
                    }
                )
                oa_data = r.json()
                with open(oa_file, 'w') as fh:
                    json.dump(oa_data, fh, indent=2)


async def get_lads(auth):
    print("Get lads (2011 Census Merged)")
    lad_file = os.path.join(CACHE_PATH, 'lads.json')
    if not os.path.exists(lad_file):
        r = await session.get(
            'https://www.nismod.ac.uk/api/data/boundaries/lads',
            auth=auth,
            params={'lad_codes': 'all'}
        )
        with open(lad_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)


async def get_oas(auth, lads):
    for lad in lads:
        lad_code = lad['lad_code']

        oa_file = os.path.join(CACHE_PATH, 'oas_by_lad',
                               'oas_{}.json'.format(lad_code))
        try:
            with open(oa_file, 'r') as fh:
                oa_data = json.load(fh)
        except FileNotFoundError:
            print("Get", lad_code)
            r = await session.get(
                'https://www.nismod.ac.uk/api/data/boundaries/oas_in_lad',
                auth=auth,
                params={'lad_codes': lad_code}
            )
            oa_data = r.json()
            with open(oa_file, 'w') as fh:
                json.dump(oa_data, fh, indent=2)


def load_lads():
    lads_json_path = os.path.join(CACHE_PATH, 'lads.json')
    with open(lads_json_path, 'r') as in_fh:
        lads = json.load(in_fh)
    return lads


def process_geographies(lads):
    lads_csv_path = os.path.join(CACHE_PATH, 'lads.csv')
    with open(lads_csv_path, 'w', newline='') as out_fh:
        lad_writer = csv.DictWriter(
            out_fh,
            fieldnames=('lad_code', 'name', 'geom'),
            extrasaction='ignore'
        )
        lad_writer.writeheader()
        lad_writer.writerows(lads)

    oas_json_path = os.path.join(CACHE_PATH, 'oas_by_lad', 'oas_{}.json')
    oas_csv_path = os.path.join(CACHE_PATH, 'oas.csv')

    with open(oas_csv_path, 'w', newline='') as out_fh:
        oa_writer = csv.DictWriter(
            out_fh,
            fieldnames=('oa_code', 'lad_code', 'geom'),
            extrasaction='ignore'
        )
        oa_writer.writeheader()
        for lad in lads:
            lad_code = lad['lad_code']
            with open(oas_json_path.format(lad_code), 'r') as in_fh:
                oas = json.load(in_fh)
                oa_writer.writerows(oas)


async def get_population(auth):
    pop_url = 'https://www.nismod.ac.uk/api/data/households/population_totals'
    for year in range(POPULATION_MIN_YEAR, POPULATION_MAX_YEAR + 1):
        print("Get oa population", year)
        oa_pop_file = get_oa_file(year)
        if not os.path.exists(oa_pop_file):
            r = await session.get(
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


def get_oa_file(year):
    return os.path.join(CACHE_PATH, 'oa_population_{}.json'.format(year))


def get_lad_file(year):
    return os.path.join(CACHE_PATH, 'lad_population_{}.json'.format(year))


def process_oa_population():
    oa_csv_path = os.path.join(CACHE_PATH, 'oa_population.csv')
    with open(oa_csv_path, 'w', newline='') as oa_fh:
        oa_writer = csv.DictWriter(
            oa_fh,
            fieldnames=('oa', 'total_population', 'year'),
            extrasaction='ignore'
        )
        oa_writer.writeheader()
        for year in range(POPULATION_MIN_YEAR, POPULATION_MAX_YEAR + 1):
            with open(get_oa_file(year), 'r') as year_fh:
                data = json.load(year_fh)
                oa_writer.writerows(data)


if __name__ == '__main__':
    session = AsyncSession(n=100)
    session.run(main)
