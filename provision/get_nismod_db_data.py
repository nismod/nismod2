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

from requests_threads import AsyncSession


MIN_YEAR = 2011
MAX_YEAR = 2020
POPULATION_DATA_VERSION = 5
CACHE_PATH = os.path.join(os.path.dirname(__file__), 'cache')


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

    await get_lads(auth)
    lads = load_lads()
    await get_oas(auth, lads)
    process_geographies(lads)

    # await get_population(auth)
    # process_lad_population()
    # process_oa_population()



async def get_lads(auth):
    print("Get lads (2011 Census Merged)")
    lad_file = os.path.join(CACHE_PATH, 'lads.json')
    if True: #not os.path.exists(lad_file):
        r = await session.get(
            'https://www.nismod.ac.uk/api/data/boundaries/lads',
            auth=auth,
            params={'lad_codes': 'all'}
        )
        with open(lad_file, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)


async def get_oas(auth, lads):
    for lad in lads:
        lad_code = lad['lad_code']

        oa_file = os.path.join(CACHE_PATH, 'oas_by_lad', 'oas_{}.json'.format(lad_code))
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
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        print("Get lad population", year)
        lad_pop_file = get_lad_file(year)
        if not os.path.exists(lad_pop_file):
            r = await session.get(
                pop_url,
                auth=auth,
                params={
                    'scale': 'lad',
                    'year': year,
                    'data_version': POPULATION_DATA_VERSION
                },
                stream=True
            )
            with open(lad_pop_file, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)

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
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)


def get_oa_file(year):
    return os.path.join(CACHE_PATH, 'oa_population_{}.json'.format(year))


def get_lad_file(year):
    return os.path.join(CACHE_PATH, 'lad_population_{}.json'.format(year))


def process_lad_population():
    lad_csv_path = os.path.join(CACHE_PATH, 'lad_population.csv')
    with open(lad_csv_path, 'w', newline='') as lad_fh:
        lad_writer = csv.DictWriter(
            lad_fh,
            fieldnames=('lad', 'total_population', 'year'),
            extrasaction='ignore'
        )
        lad_writer.writeheader()
        for year in range(MIN_YEAR, MAX_YEAR + 1):
            with open(get_lad_file(year), 'r') as year_fh:
                data = json.load(year_fh)
                lad_writer.writerows(data)


def process_oa_population():
    oa_csv_path = os.path.join(CACHE_PATH, 'oa_population.csv')
    with open(oa_csv_path, 'w', newline='') as oa_fh:
        oa_writer = csv.DictWriter(
            oa_fh,
            fieldnames=('oa', 'total_population', 'year'),
            extrasaction='ignore'
        )
        oa_writer.writeheader()
        for year in range(MIN_YEAR, MAX_YEAR + 1):
            with open(get_oa_file(year), 'r') as year_fh:
                data = json.load(year_fh)
                oa_writer.writerows(data)


if __name__ == '__main__':
    session = AsyncSession(n=100)
    session.run(main)
