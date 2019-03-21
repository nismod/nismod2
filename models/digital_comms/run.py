"""Digital demand dummy model
"""
import configparser
import csv
import os

import fiona  # type: ignore
import numpy as np  # type: ignore

from digital_comms.fixed_network.model import NetworkManager
from digital_comms.runner import read_csv, read_assets, read_links

from smif.model.sector_model import SectorModel  # type: ignore
from smif.data_layer import DataHandle

class DigitalCommsWrapper(SectorModel):
    """Digital model
    """
    def __init__(self, name):
        super().__init__(name)
        self.system = None

    def before_model_run(self, data_handle : DataHandle):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)
        """
        print('before model run')

        # Get wrapper configuration
        path_main = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))
        data_path = config['PATHS']['path_local_data']

        # Get modelrun configuration
        read_only_parameters = data_handle.get_parameters()

        parameters = {}
        for name, dataarray in read_only_parameters.items():
            parameters[name] = dataarray.data

        self.logger.debug(parameters)

        # Load assets
        assets = read_assets(data_path)

        # Load links
        links = read_links(data_path)

        self.logger.info("DigitalCommsWrapper - Intitialise system")
        self.system = NetworkManager(assets, links, parameters)

        print('only distribution points with a benefit cost ratio > 1 can be upgraded')
        print('model rollout is constrained by the adoption desirability set by scenario')

    def simulate(self, data_handle : DataHandle):
        """Implement smif.SectorModel simulate
        """
        # -----
        # Start
        # -----
        data_handle = data_handle
        now = data_handle.current_timestep
        self.logger.info("DigitalCommsWrapper received inputs in %s", now)

        interventions = data_handle.get_current_interventions()

        self.logger.debug("DigitalCommsWrapper - Upgrading system")
        self.system.upgrade(interventions)

        # -------------
        # Write outputs
        # -------------
        coverage = self.system.coverage()
        aggregate_coverage = self.system.aggregate_coverage()
        capacity = self.system.capacity()
        spend = self.system.spend()

        data_handle.set_results('coverage', coverage)
        data_handle.set_results('aggregate_coverage', aggregate_coverage)
        data_handle.set_results('capacity', capacity)
        data_handle.set_results('spend', spend)
