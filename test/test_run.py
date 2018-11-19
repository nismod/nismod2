"""Test sets of model configuration files for run without error
"""
import os
import shutil
from subprocess import run

from pytest import mark


# Base directory
NISMOD_DIR = os.path.join(os.path.dirname(__file__), '..')


def model_configuration_run(modelrun_name):
    """Run `smif.cli.execute_model_run` on a model_configuration
       - Clear results
       - Run model
       - Expect results and no errors
    """
    # Clear results
    results_folder = os.path.join(NISMOD_DIR, 'results')
    if os.path.isdir(results_folder):
        for file in os.listdir(results_folder):
            file_path = os.path.join(results_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(e)

    # Run Model
    run("smif run "  + modelrun_name + " -d" + NISMOD_DIR, shell=True, check=True)

    # Expect results
    assert os.path.isdir(os.path.join(results_folder, modelrun_name))


def check_result_exists(modelrun_name, sector_model_name, decision_iteration, result_file_name):
    """ Check if a certain result file was generated a modelrun
    """
    config_dirname = os.path.join(NISMOD_DIR, 'results')
    results_folder = os.path.join(
        config_dirname,
        modelrun_name,
        sector_model_name,
        decision_iteration
    )
    assert os.path.exists(os.path.join(results_folder, result_file_name))


def test_digital_comms_run():
    model_configuration_run('digital_comms_b_fttdp_r')

    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_distribution_upgrade_costs_fttdp_timestep_2020.csv')
    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_distribution_upgrades_timestep_2020.csv')
    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_lad_premises_with_fttdp_timestep_2020.csv')
    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_distribution_upgrade_costs_fttdp_timestep_2020.csv')
    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_lad_premises_with_fttp_timestep_2020.csv')
    check_result_exists('digital_comms_b_fttdp_r', 'digital_comms_fixed_network', 'decision_0',
                        'output_percentage_of_premises_connected_with_fttdp_timestep_2020.csv')

@mark.skip
def test_energy_demand_run():
    model_configuration_run('energy_demand_test')

@mark.skip
def test_energy_supply_run():
    model_configuration_run('energy_supply_test')

@mark.skip
def test_transport_run():
    model_configuration_run('transport_southampton')


@mark.skip
def test_solid_waste_run():
    model_configuration_run('solid_waste_minimal')


@mark.skip
def test_water_supply_run():
    model_configuration_run('water_supply_minimal')


@mark.skip
def test_energy_transport_dependency_run():
    model_configuration_run('energy_transport_dependency')


@mark.skip
def test_sos_run():
    model_configuration_run('sos_minimal')
