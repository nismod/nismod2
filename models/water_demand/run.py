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

        # The populations and demands are currently scenario dependencies
        population = data_handle.get_data('population')
        per_capita = data_handle.get_data('per_capita_water_demand')
        constant = data_handle.get_data('constant_water_demand')

        # Create the model
        model = WaterDemand(
            population=population.data,
            per_capita_demand=per_capita.data,
            constant_demand=constant.data
        )

        # Simulate the water demand
        demand = model.simulate()

        data_handle.set_results('water_demand', demand)
