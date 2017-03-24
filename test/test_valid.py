"""Test sets of model configuration files for validity
"""
import os
from glob import glob
from unittest.mock import MagicMock

from smif.cli import validate_config

def test_model_configurations_valid():
    test_dir = os.path.dirname(__file__)
    model_config_files = glob(
        os.path.join(
            str(test_dir),
            "model_configurations",
            "**",
            "model.yaml"))
    for model_config in model_config_files:
        mock_args = MagicMock()
        mock_args.path = model_config
        validate_config(mock_args)

if __name__ == '__main__':
    test_model_configurations_valid()