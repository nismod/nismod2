"""
The settings module which points the settings at environment variables.
"""
import os
from pathlib import Path


# Static settings
INPUT_PATH = Path("/data/inputs/")
OUTPUT_PATH = Path("/data/outputs/")
CONFIG_FILE = Path("/code/script_config.ini")
RESULTS_PATH = Path("/code/nismod2/results/")
NISMOD_PATH = Path("/code/nismod2/")
NISMOD_DATA_PATH = NISMOD_PATH.joinpath("data/")
TRANSPORT_ADDITIONAL_OUTPUTS_PATH = NISMOD_DATA_PATH.joinpath("transport/gb/output/")
NISMOD_SCENARIOS_PATH = NISMOD_DATA_PATH.joinpath("scenarios/")
NISMOD_SOCIO_ECONOMIC_PATH = NISMOD_SCENARIOS_PATH.joinpath("socio-economic/")

# User settable settings
model_to_run = os.getenv("model_to_run", "error")
part_of_sos_model = os.getenv("part_of_sos_model", False)
sector_model = os.getenv("sector_model", "error")
timestep = os.getenv("timestep", "")
transforms_to_run = os.getenv("transforms_to_run", "[]")
use_generated_scenario = os.getenv("use_generated_scenario", False)
