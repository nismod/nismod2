"""{model_name_cap} wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel


class {model_name_cap}Wrapper(SectorModel):
    """{model_name_cap}
    """
    def initialise(self, initial_conditions):
        pass

    def simulate(self, data):

        # Get the current timestep
        now = data.current_timestep
        self.logger.info("{model_name_cap}Wrapper received inputs in %s", now)

        # Get model parameters
        {model_parameters}
        # Get model inputs
        {model_inputs}
        # Write results to data handler
        {model_outputs}
        self.logger.info("{model_name_cap}Wrapper produced outputs in %s", now)

    def extract_obj(self, results):
        return 0