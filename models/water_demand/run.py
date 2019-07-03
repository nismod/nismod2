"""Water demand model
"""
import numpy as np
import pandas as pd

from smif.model.sector_model import SectorModel
from water_demand import WaterDemand


class WaterDemandWrapper(SectorModel):
    """Water Model Wrapper
    """

    def before_model_run(self, data_handle=None):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        pass

    def simulate(self, data_handle):
        """Runs the water supply model.

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        """

        # The per capita demand (in ML/person/day) is set as a model parameter
        per_capita_demand = data_handle.get_parameter('per_capita_water_demand')

        # The population is currently a scenario dependency
        pop_input = data_handle.get_data('population')

        # Create the model
        model = WaterDemand(population=pop_input.data, scale_factor=per_capita_demand.data)

        # Simulate the water demand
        demand = model.simulate()

        data_handle.set_results('water_demand', demand)
