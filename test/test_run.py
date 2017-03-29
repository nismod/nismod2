"""Test sets of model configuration files for run without error
"""
import os
from glob import glob
from unittest.mock import MagicMock

from smif.cli import run_model

def model_configuration_run(config_dirname):
    """Run `smif.cli.run_model` on a model_configuration, expect no errors
    """
    test_dir = os.path.dirname(__file__)
    model_config = os.path.join(
        str(test_dir),
        "model_configurations",
        config_dirname,
        "model.yaml"
    )
    mock_args = MagicMock()
    mock_args.path = model_config
    mock_args.model = 'all'
    mock_args.output_file = '/tmp/results.yaml'
    run_model(mock_args)


def test_digital_comms_run():
    model_configuration_run('digital_comms_minimal')


def test_energy_demand_run():
    model_configuration_run('energy_demand_minimal')


def test_energy_supply_run():
    model_configuration_run('energy_supply_minimal')


def test_solid_waste_run():
    model_configuration_run('solid_waste_minimal')


def test_transport_run():
    model_configuration_run('transport_minimal')


def test_water_supply_run():
    model_configuration_run('water_supply_minimal')


def test_energy_transport_dependency_run():
    model_configuration_run('energy_transport_dependency')


def test_sos_run():
    model_configuration_run('sos_minimal')


if __name__ == '__main__':
    test_digital_comms_run()
    test_energy_demand_run()
    test_energy_supply_run()
    test_solid_waste_run()
    test_transport_run()
    test_water_supply_run()
    test_energy_transport_dependency_run()
    test_sos_run()
