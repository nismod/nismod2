from utils import run_process, link_files, copy_lads
from shutil import unpack_archive
from pathlib import Path
from settings import (
    NISMOD_PATH,
    NISMOD_DATA_PATH,
    NISMOD_SCENARIOS_PATH,
    NISMOD_SOCIO_ECONOMIC_PATH,
)


def extract():
    copy_lads()

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
        # {
        #     "src": "/data/energy_supply/energy_supply_data_v0.9.10.zip",
        #     "dest": str(NISMOD_DATA_PATH.joinpath("energy_supply/")),
        # },
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

    print("Installing energy_demand")
    run_process(
        "cd "
        + str(NISMOD_PATH)
        + " && ./provision/install_energy_demand.sh "
        + str(NISMOD_PATH)
    )
    print("energy_demand setup")
    run_process(
        "cd "
        + str(NISMOD_PATH)
        + " && energy_demand setup -f "
        + str(NISMOD_PATH)
        + "/models/energy_demand/wrapperconfig.ini"
    )
