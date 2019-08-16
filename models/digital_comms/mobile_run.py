"""Digital demand dummy model
"""
import configparser
import csv
import os

from digital_comms.mobile_network.model import NetworkManager
from smif.model import SectorModel

class DigitalMobileWrapper(SectorModel):
    def simulate(self, data_handle):
        self.logger.debug("Running {} timestep {}".format(self.__class__, data_handle.current_timestep))

        self.logger.debug("INPUTS")
        self.logger.debug(self.inputs)
