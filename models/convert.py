
"""Energy supply wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel
from subprocess import check_output
import os
import psycopg2
from collections import namedtuple
from smif.convert import SpaceTimeUnitConvertor
import logging

class InputOutputConvertor(SpaceTimeUnitConvertor):

    def __init__(self):
        super().__init__()

    def convert_data(self, data_handle, model_input, model_output):
        """Convert between resolutions
        """
        self.logger.info("Converting data for input '%s'",
                         model_input.name)

        data = data_handle.get_data(model_input.name)

        from_spatial = model_input.spatial_resolution.name
        from_temporal = model_input.temporal_resolution.name
        from_unit = model_input.units

        to_spatial = model_output.spatial_resolution.name
        to_temporal = model_output.temporal_resolution.name
        to_unit = model_output.units

        self.logger.debug("Converting from %s to %s",
            from_temporal, to_temporal)

        self.logger.debug("Coverting from %s to %s",
            from_spatial, to_spatial)

        self.logger.debug("Coverting from %s to %s",
            from_unit, to_unit)

        space_time_result = SpaceTimeUnitConvertor.convert(
            self,
            data,
            from_spatial,
            to_spatial,
            from_temporal,
            to_temporal,
            from_unit,
            to_unit)

        return space_time_result

class ConvertDemandToSupply(SectorModel):
    """Converts energy demand data to energy supply
    """
    def simulate(self, data_handle):
        """Convert data between configured resolutions
        """
        convertor = InputOutputConvertor()

        for input_name, model_input in self.inputs.items():
            self.logger.debug("Model input: %s", model_input)
            model_output = self.outputs[input_name]
            results = convertor.convert_data(data_handle,
                                             model_input,
                                             model_output)

            data_handle.set_results(input_name, results)
