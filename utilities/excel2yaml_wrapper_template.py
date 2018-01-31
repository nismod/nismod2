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

        # Demonstrates how to get the value for a model input
        # (defaults to the current time period)
        current_{model_name} = data.get_data('{model_name}')
        self.logger.info("Current {model_name_rm_} in %s is %s",
                         now, current_{model_name})

        # Demonstrates how to get the value for a model input from the base
        # timeperiod
        base_{model_name} = data.get_base_timestep_data('{model_name}')
        base_year = data.base_timestep
        self.logger.info("Base year {model_name_rm_} in %s was %s", base_year,
                         base_{model_name})

        # Demonstrates how to get the value for a model input from the previous
        # timeperiod
        if now > base_year:
            prev_{model_name} = data.get_previous_timestep_data('{model_name}')
            prev_year = data.previous_timestep
            self.logger.info("Previous {model_name_rm_} in %s was %s",
                             prev_year, prev_{model_name})

        # Pretend to call the '{model_name_rm_}'
        # This code prints out debug logging messages for each input
        # defined in the {model_name} configuration
        for name in self.inputs.names:
            time_intervals = self.inputs[name].get_interval_names()
            regions = self.inputs[name].get_region_names()
            for i, region in enumerate(regions):
                for j, interval in enumerate(time_intervals):
                    self.logger.info(
                        "%s %s %s",
                        interval,
                        region,
                        data.get_data(name)[i, j])

        # Write pretend results to data handler
        {model_outputs}
        self.logger.info("{model_name_cap}Wrapper produced outputs in %s",
                         now)

    def extract_obj(self, results):
        return 0