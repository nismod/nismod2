"""Test sets of model configuration files for run without error
"""
import os, shutil
from glob import glob
from unittest.mock import MagicMock

from smif.cli import execute_model_run

def model_configuration_run(config_dirname, modelrun_name):
    """Run `smif.cli.execute_model_run` on a model_configuration
       - Clear results
       - Run model
       - Expect results and no errors
    """
    test_dir = os.path.dirname(__file__)
    model_config = os.path.join(
        str(test_dir),
        "model_configurations",
        config_dirname
    )

    # Clear results
    results_folder = os.path.join(model_config, 'results')
    for file in os.listdir(results_folder):
        file_path = os.path.join(results_folder, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

    # Run Model
    mock_args = MagicMock()
    mock_args.directory = model_config
    mock_args.modelrun = modelrun_name
    execute_model_run(mock_args)

    # Expect results
    assert os.path.isdir(os.path.join(results_folder, modelrun_name))


def check_result_exists(config_dirname, modelrun_name, sector_model_name, result_file_name):
    """ Check if a certain result file was generated a modelrun
    """
    test_dir = os.path.dirname(__file__)
    results_folder = os.path.join(
        str(test_dir),
        "model_configurations",
        config_dirname,
        'results'
    )

    assert os.path.exists(os.path.join(results_folder, modelrun_name, sector_model_name, result_file_name))


# def test_digital_comms_run():
#     model_configuration_run('digital_comms_minimal')


def test_energy_demand_minimal_run():
    model_configuration_run('energy_demand_minimal', 'energy_demand_test')

    check_result_exists('energy_demand_minimal', 'energy_demand_test', 'energy_demand', 
                        'output_residential_solid_fuel_boiler_solid_fuel_timestep_2015_regions_national_intervals_hourly.csv')
    check_result_exists('energy_demand_minimal', 'energy_demand_test', 'energy_demand', 
                        'output_residential_solid_fuel_boiler_solid_fuel_timestep_2016_regions_national_intervals_hourly.csv')


# def test_energy_supply_run():
#     model_configuration_run('energy_supply_minimal')


# def test_solid_waste_run():
#     model_configuration_run('solid_waste_minimal')


# def test_transport_run():
#     model_configuration_run('transport_minimal')


# def test_water_supply_run():
#     model_configuration_run('water_supply_minimal')


# def test_energy_transport_dependency_run():
#     model_configuration_run('energy_transport_dependency')


# def test_sos_run():
#     model_configuration_run('sos_minimal')


if __name__ == '__main__':
    test_digital_comms_run()
    test_energy_demand_run()
    test_energy_supply_run()
    test_solid_waste_run()
    test_transport_run()
    test_water_supply_run()
    test_energy_transport_dependency_run()
    test_sos_run()
