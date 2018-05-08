"""Test sets of model configuration files for run without error

Example manual usage to run transport_minimal with debug logging::

    python test/test_run.py -vv --tr
"""
import os, shutil, sys
from glob import glob
from subprocess import run

from smif.cli import execute_model_run

def model_configuration_run(config_dirname, modelrun_name):
    """Run `smif.cli.execute_model_run` on a model_configuration
       - Clear results
       - Run model
       - Expect results and no errors
    """

    # Clear results
    results_folder = os.path.join(config_dirname, 'results')
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
    run("smif run "  + modelrun_name + " -d" + config_dirname, shell=True, check=True)

    # Expect results
    assert os.path.isdir(os.path.join(results_folder, modelrun_name))


def check_result_exists(config_dirname, modelrun_name, sector_model_name, result_file_name):
    """ Check if a certain result file was generated a modelrun
    """
    results_folder = os.path.join(
        config_dirname,
        modelrun_name,
        os.listdir(os.path.join(config_dirname, modelrun_name))[0],
        sector_model_name
    )

    files = os.listdir(results_folder)
    assert os.path.exists(os.path.join(results_folder, result_file_name))


def test_digital_comms_run():
    model_configuration_run('/vagrant', 'digital_comms_test')

    check_result_exists(os.path.join('/vagrant', 'results'), 'digital_comms_test', 'digital_comms',
                        'output_distribution_upgrade_costs_fttp_timestep_2015_regions_broadband_distributions_intervals_annual.dat')
    check_result_exists(os.path.join('/vagrant', 'results'), 'digital_comms_test', 'digital_comms',
                        'output_distribution_upgrade_costs_fttp_timestep_2020_regions_broadband_distributions_intervals_annual.dat')
    check_result_exists(os.path.join('/vagrant', 'results'), 'digital_comms_test', 'digital_comms',
                        'output_distribution_upgrades_timestep_2015_regions_broadband_distributions_intervals_annual.dat')
    check_result_exists(os.path.join('/vagrant', 'results'), 'digital_comms_test', 'digital_comms',
                        'output_distribution_upgrades_timestep_2020_regions_broadband_distributions_intervals_annual.dat')                        


def test_energy_demand_run():
    model_configuration_run('/vagrant', 'energy_demand_test')


def test_energy_supply_run():
    model_configuration_run('/vagrant', 'energy_supply_test')


def test_solid_waste_run():
    # model_configuration_run('solid_waste_minimal')
    pass


def test_transport_run():
    model_configuration_run('/vagrant', 'transport_test')


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
