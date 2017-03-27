"""Test sets of model configuration files for validity
"""
import os
from glob import glob
from unittest.mock import MagicMock

from smif.cli import validate_config

def model_configuration_valid(config_dirname):
    """Run `smif.cli.validate_config` on a model_configuration, expect no errors
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
    validate_config(mock_args)


def test_digital_comms_valid():
    model_configuration_valid('digital_comms_minimal')


def test_energy_demand_valid():
    model_configuration_valid('energy_demand_minimal')


def test_energy_supply_valid():
    model_configuration_valid('energy_supply_minimal')


def test_solid_waste_valid():
    model_configuration_valid('solid_waste_minimal')


def test_transport_valid():
    model_configuration_valid('transport_minimal')


def test_water_supply_valid():
    model_configuration_valid('water_supply_minimal')


def test_energy_transport_dependency_valid():
    model_configuration_valid('energy_transport_dependency')


def test_sos_valid():
    model_configuration_valid('sos_minimal')


if __name__ == '__main__':
    test_digital_comms_valid()
    test_energy_demand_valid()
    test_energy_supply_valid()
    test_solid_waste_valid()
    test_transport_valid()
    test_water_supply_valid()
    test_energy_transport_dependency_valid()
    test_sos_valid()
