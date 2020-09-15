import os
import time
import sys
import importlib.util
import psycopg2
from utils import run_process, link_files
from shutil import unpack_archive, move
from pathlib import Path
from settings import (
    NISMOD_PATH,
    NISMOD_DATA_PATH,
    NISMOD_SCENARIOS_PATH,
    NISMOD_SOCIO_ECONOMIC_PATH,
)


spec = importlib.util.spec_from_file_location(
    "run_migrations", "/code/nismod2/install/energy_supply/run_migrations.py"
)
run_migrations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(run_migrations)


def configure_database():
    print("Install ODBC")
    run_process(
        "cd /code/nismod2 && odbcinst -i -s -f /code/nismod2/install/odbc_config.ini"
    )
    print("ODBC Installed")

    DB_NAME = os.getenv("PGDATABASE", "postgres")
    USER = os.getenv("PGUSER", "postgres")
    PASSWORD = os.getenv("PGPASSWORD", "postgres")
    HOST = os.getenv("PGHOST", "0.0.0.0")
    PORT = int(os.getenv("PGPORT", "5432"))
    retry = 1
    while retry < 11:
        print(f"Trying database {retry} times")
        retry = retry + 1
        try:
            connection = psycopg2.connect(
                dbname=DB_NAME, user=USER, password=PASSWORD, host=HOST, port=PORT,
            )
            cur = connection.cursor()
            cur.execute("SELECT 1")
        except psycopg2.OperationalError:
            time.sleep(10)
            print("Database not up waiting 10 seconds")
            continue
        print("Database up")
        break

    if retry == 10:
        print("Database not up after 10 tries")
        sys.exit(1)


def execute_migrations():
    print("Migrations START")
    # directories and files
    MIGRATIONS_DIR = "/code/nismod2/install/energy_supply/migrations"
    DATA_DIR = "/code/nismod2/data/energy_supply/database_full"
    print(MIGRATIONS_DIR)
    print(DATA_DIR)

    up_migration_files, down_migration_files = run_migrations.find_files(MIGRATIONS_DIR)

    down_migration_files.reverse()
    # run_migrations.run_migrations(down_migration_files, MIGRATIONS_DIR)
    run_migrations.run_migrations(up_migration_files, MIGRATIONS_DIR)
    run_migrations.load_data(up_migration_files, DATA_DIR)
    run_migrations.final_setup()
    print("Migrations END")


def install_FICO():
    print("Installing FICO")
    run_process("code/xpress_setup/install.sh -l static -a /code/xpress/xpauth.xpr -d /opt/xpressmp -k no")
    run_process(". /opt/xpressmp/bin/xpvars.sh")
    print("Installed FICO")


def extract():
    install_FICO()
    print("Copying LADS")
    lads_input = Path("/data/lads/")
    lads_output = NISMOD_DATA_PATH.joinpath("dimensions/")
    run_process("cp -ru " + str(lads_input) + "/ " + str(lads_output))
    print("Finished Copying LADS")

    print("Extracting")
    datasets = [
        {
            "src": "/data/scenarios/climate_v1.zip",
            "dest": str(NISMOD_SCENARIOS_PATH.joinpath("climate/")),
        },
        {
            "src": "/data/scenarios/population_v1.zip",
            "dest": str(NISMOD_SCENARIOS_PATH.joinpath("population/")),
        },
        {
            "src": "/data/scenarios/prices_v2.zip",
            "dest": str(NISMOD_SCENARIOS_PATH.joinpath("prices/")),
        },
        {
            "src": "/data/scenarios/socio-economic-1.0.1.zip",
            "dest": str(NISMOD_SOCIO_ECONOMIC_PATH),
        },
        {
            "src": "/data/scenarios/ev_transport_trips_v0.1.zip",
            "dest": str(NISMOD_SCENARIOS_PATH.joinpath("ev_transport_trips/")),
        },
        {
            "src": "/data/energy_supply/energy_supply_data_v0.9.10.zip",
            "dest": str(NISMOD_DATA_PATH.joinpath("energy_supply/")),
        },
        {
            "src": "/data/energy_demand/v0.9.12_full.zip",
            "dest": str(NISMOD_DATA_PATH.joinpath("energy_demand/")),
        },
        {
            "src": "/data/energy_demand/config_data_v1.0.zip",
            "dest": str(NISMOD_DATA_PATH.joinpath("energy_demand/config_data/")),
        },
    ]
    for data in datasets:
        print("Extracting - " + data["src"] + " - to - " + data["dest"])
        unpack_archive(data["src"], data["dest"], "zip")

    link_files(
        Path.joinpath(NISMOD_SOCIO_ECONOMIC_PATH, "socio-economic-1.0.1/"),
        NISMOD_SOCIO_ECONOMIC_PATH,
    )

    configure_database()
    execute_migrations()
