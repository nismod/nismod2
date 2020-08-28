import os
import yaml
from pathlib import Path
from extract_data import extract
from utils import run_process, is_truthy
from settings import (
    INPUT_PATH,
    NISMOD_PATH,
    RESULTS_PATH,
    model_to_run,
    part_of_sos_model,
    sector_model,
    timestep,
    use_generated_scenario,
)


def extract_and_run():
    extract()

    go_to_nismod_root = "cd " + str(NISMOD_PATH)
    
    print("Deciding   -   ", model_to_run)
    run_process(go_to_nismod_root + " && smif list")
    run_process(go_to_nismod_root + " && smif decide " + model_to_run)
    print("Decided woop!")
