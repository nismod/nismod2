from utils import run_process, link_files
from shutil import unpack_archive
from pathlib import Path
from settings import (
    NISMOD_PATH,
    NISMOD_DATA_PATH,
    NISMOD_SCENARIOS_PATH,
    NISMOD_SOCIO_ECONOMIC_PATH,
)


def extract():
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
            "src": "/data/et_module/et_module_v0.5.zip",
            "dest": str(NISMOD_DATA_PATH.joinpath("et_module/")),
        },
    ]
    for data in datasets:
        print("Extracting - " + data["src"] + " - to - " + data["dest"])
        unpack_archive(data["src"], data["dest"], "zip")

    link_files(
        Path.joinpath(NISMOD_SOCIO_ECONOMIC_PATH, "socio-economic-1.0.1/"),
        NISMOD_SOCIO_ECONOMIC_PATH,
    )

    print("Installing ET Module")
    run_process(
        "cd "
        + str(NISMOD_PATH)
        + " && ./provision/install_et_module.sh "
        + str(NISMOD_PATH)
    )