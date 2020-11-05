import importlib.util
from utils import run_process, link_files, copy_lads
from shutil import unpack_archive, move, rmtree, move
from pathlib import Path
from settings import (
    NISMOD_PATH,
    NISMOD_DATA_PATH,
    NISMOD_SCENARIOS_PATH,
    NISMOD_SOCIO_ECONOMIC_PATH,
)

spec = importlib.util.spec_from_file_location(
    "convert_transport_engine_fractions",
    str(
        NISMOD_PATH.joinpath(
            "utilities/transport/convert_transport_engine_fractions.py"
        )
    ),
)
convert_transport_engine_fractions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(convert_transport_engine_fractions)


def extract():
    copy_lads() 

    print("Extracting")
    TRANSPORT_PATH = NISMOD_DATA_PATH.joinpath("transport/")
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
        # {
        #     "src": "/data/energy_demand/v0.9.12_full.zip",
        #     "dest": str(NISMOD_DATA_PATH.joinpath("energy_demand/")),
        # },
        # {
        #     "src": "/data/energy_demand/config_data_v1.0.zip",
        #     "dest": str(NISMOD_DATA_PATH.joinpath("energy_demand/config_data/")),
        # },
        {
            "src": "/data/transport/TR_data_full_for_release_v2.3.0.zip",
            "dest": str(TRANSPORT_PATH),
        },
        {
            "src": "/data/transport/transport_testdata_2.3.0.zip",
            "dest": str(TRANSPORT_PATH),
        },
        {
            "src": "/data/transport/transport-rail_v1.0.0.zip",
            "dest": str(TRANSPORT_PATH),
        },
    ]
    for data in datasets:
        print("Extracting - " + data["src"] + " - to - " + data["dest"])
        unpack_archive(data["src"], data["dest"], "zip")

    link_files(
        Path.joinpath(NISMOD_SOCIO_ECONOMIC_PATH, "socio-economic-1.0.1/"),
        NISMOD_SOCIO_ECONOMIC_PATH,
    )

    print("Moving TR_data_full")
    TR_DATA_FULL_PATH = TRANSPORT_PATH.joinpath("TR_data_full/")
    rmtree(str(TR_DATA_FULL_PATH), ignore_errors=True)
    move(
        str(TRANSPORT_PATH.joinpath("TR_data_full_for_release_v2.3.0/")),
        str(TR_DATA_FULL_PATH),
    )

    print("Moving TR GB data")
    TR_GB_PATH = TRANSPORT_PATH.joinpath("gb/")
    TR_GB_DATA_PATH = TR_GB_PATH.joinpath("data")
    rmtree(str(TR_GB_PATH), ignore_errors=True)
    TR_GB_PATH.joinpath("config").parent.mkdir(parents=True, exist_ok=True)
    move(str(TR_DATA_FULL_PATH.joinpath("full/data")), str(TR_GB_DATA_PATH))

    print("Moving Southampton data")
    SOUTHAMPTON_PATH = TRANSPORT_PATH.joinpath("southampton/")
    rmtree(str(SOUTHAMPTON_PATH), ignore_errors=True)
    SOUTHAMPTON_PATH.joinpath("config").parent.mkdir(parents=True, exist_ok=True)
    move(
        str(TRANSPORT_PATH.joinpath("transport_testdata_2.3.0/")),
        str(SOUTHAMPTON_PATH.joinpath("data/")),
    )
    print("southampton Data directory looks like")
    for dc in SOUTHAMPTON_PATH.joinpath("data/").iterdir():
        print(str(dc))
    for dc in SOUTHAMPTON_PATH.joinpath("data/csvfiles/").iterdir():
        print(str(dc))

    print("Gzipping passengerRoutes")
    run_process("gzip " + str(SOUTHAMPTON_PATH.joinpath("data/routes/passengerRoutes.dat")))
    print("Gzipping freightRoutes")
    run_process("gzip " + str(SOUTHAMPTON_PATH.joinpath("data/routes/freightRoutes.dat")))

    print("Converting Engine fractions")
    convert_transport_engine_fractions.main(
        str(TR_GB_DATA_PATH.joinpath("csvfiles/engineTypeFractions.csv")),
        str(NISMOD_SCENARIOS_PATH.joinpath("engine_type_fractions.csv")),
    )
    convert_transport_engine_fractions.main(
        str(TR_GB_DATA_PATH.joinpath("csvfiles/engineTypeFractionsEW.csv")),
        str(NISMOD_SCENARIOS_PATH.joinpath("engine_type_fractions_ew.csv")),
    )
    convert_transport_engine_fractions.main(
        str(TR_GB_DATA_PATH.joinpath("csvfiles/engineTypeFractionsMVE.csv")),
        str(NISMOD_SCENARIOS_PATH.joinpath("engine_type_fractions_mve.csv")),
    )

    print("Moving rail data")
    rail_data = [
        "dimensions/",
        "initial_conditions/",
        "interventions/",
        "parameters/",
        "scenarios/",
    ]
    TRANSPORT_RAIL_PATH = TRANSPORT_PATH.joinpath("transport-rail_v1.0.0/")
    for rd in rail_data:
        src_path = str(TRANSPORT_RAIL_PATH.joinpath(rd))
        dest_path = str(NISMOD_DATA_PATH.joinpath(rd))
        print("Moving - " + src_path + " - to - " + dest_path)
        move(src_path, dest_path)

    # print("energy_demand setup")
    # run_process(
    #     "cd "
    #     + str(NISMOD_PATH)
    #     + " && energy_demand setup -f "
    #     + str(NISMOD_PATH)
    #     + "/models/energy_demand/wrapperconfig.ini"
    # )
