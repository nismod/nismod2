"""
The Job Processing Wrapper will be called from the Queue Processing Daemon
when a new job is received. The wrapper will first get the parameters from the
database and set them in the configuration file. It will then run the model with
parameters set in the config file. The results of the model run will then be extracted
and pushed to the database. The result of running the job (success or fail) will then
be returned to the queue_processing_daemon which will update the status of the
job in the database.
"""
# pylint: disable=W0703, E0602, E0401
from shutil import copyfile, rmtree, copytree
from run_nismod import extract_and_run
from utils import run_process, is_truthy
from settings import (
    INPUT_PATH,
    CONFIG_FILE,
    NISMOD_PATH,
    NISMOD_DATA_PATH,
    NISMOD_SCENARIOS_PATH,
    NISMOD_SOCIO_ECONOMIC_PATH,
    part_of_sos_model,
    sector_model,
    timestep,
    use_generated_scenario,
    OUTPUT_PATH,
    RESULTS_PATH,
    model_to_run,
)


def process_job():
    """
    The main function which will be called to change the parameters file and create
    the necessary directories.
    """
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("Running with following settings:")
    print("INPUT_PATH  -  ", str(INPUT_PATH))
    print("CONFIG_FILE  -  ", str(CONFIG_FILE))
    print("NISMOD_PATH  -  ", str(NISMOD_PATH))
    print("NISMOD_DATA_PATH  -  ", str(NISMOD_DATA_PATH))
    print("NISMOD_SCENARIOS_PATH  -  ", str(NISMOD_SCENARIOS_PATH))
    print("NISMOD_SOCIO_ECONOMIC_PATH  -  ", str(NISMOD_SOCIO_ECONOMIC_PATH))
    print("OUTPUT_PATH  -  ", str(OUTPUT_PATH))
    print("RESULTS_PATH  -  ", str(RESULTS_PATH))
    print("model_to_run  -  ", str(model_to_run))
    print("part_of_sos_model  -  ", str(part_of_sos_model))
    print("sector_model  -  ", str(sector_model))
    print("timestep  -  ", str(timestep))
    print("use_generated_scenario  -  ", str(use_generated_scenario))

    # Extract the data and run the nismod model
    extract_and_run()
    print("Finished model run")

    # Copy results across to expected path for DAFNI
    results_dir = RESULTS_PATH.joinpath(model_to_run)
    run_process("cp -r " + str(results_dir) + "/ " + str(OUTPUT_PATH))
    print("Copied results")


if __name__ == "__main__":
    process_job()
