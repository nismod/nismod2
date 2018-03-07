"""Test sets of model configuration files for run without error

Example manual usage to run transport_minimal with debug logging::

    python test/test_run.py -vv --tr
"""
import os, shutil, sys
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
    if os.path.isdir(results_folder):
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


def test_digital_comms_run():
    # model_configuration_run('digital_comms_minimal')
    pass


def test_energy_demand_run():
    model_configuration_run('energy_demand_minimal', 'energy_demand_test')

    check_result_exists('energy_demand_minimal', 'energy_demand_test', 'energy_demand',
                        'output_residential_solid_fuel_boiler_solid_fuel_timestep_2015_regions_national_intervals_hourly.csv')
    check_result_exists('energy_demand_minimal', 'energy_demand_test', 'energy_demand',
                        'output_residential_solid_fuel_boiler_solid_fuel_timestep_2016_regions_national_intervals_hourly.csv')


def test_energy_supply_run():
    # model_configuration_run('energy_supply_minimal')
    pass


def test_solid_waste_run():
    # model_configuration_run('solid_waste_minimal')
    pass


def test_transport_run():
    model_configuration_run('transport_minimal', 'transport_test')

    check_result_exists('transport_minimal', 'transport_test', 'transport',
                        'output_energy-consumption_DIESEL_timestep_2015_regions_whole_system_intervals_annual_day.dat')


def test_water_supply_run():
    # model_configuration_run('water_supply_minimal')
    pass


def test_energy_transport_dependency_run():
    # model_configuration_run('energy_transport_dependency')
    pass


def test_sos_run():
    # model_configuration_run('sos_minimal')
    pass


if __name__ == '__main__':
    if '--dc' in sys.argv:
        test_digital_comms_run()
    if '--ed' in sys.argv:
        test_energy_demand_run()
    if '--es' in sys.argv:
        test_energy_supply_run()
    if '--sw' in sys.argv:
        test_solid_waste_run()
    if '--tr' in sys.argv:
        test_transport_run()
    if '--ws' in sys.argv:
        test_water_supply_run()
    if '--et' in sys.argv:
        test_energy_transport_dependency_run()
    if '--sos' in sys.argv:
        test_sos_run()
