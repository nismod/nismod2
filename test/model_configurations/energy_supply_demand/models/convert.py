
"""Energy supply wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel
from subprocess import check_output
import os
import psycopg2
from collections import namedtuple
from smif.convert import SpaceTimeConvertor, UnitConvertor
import logging

class InputOutputConvertor(SpaceTimeConvertor, UnitConvertor):

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        SpaceTimeConvertor.__init__(self)
        UnitConvertor.__init__(self)

    def convert_data(self, data_handle, model_input, model_output):

        self.logger.info("Converting data for input '%s'",
                         model_input.name)

        data = data_handle.get_data(model_input.name)

        from_spatial = model_input.spatial_resolution
        from_temporal = model_input.temporal_resolution
        from_unit = model_input.units

        to_spatial = model_output.spatial_resolution
        to_temporal = model_output.temporal_resolution
        to_unit = model_output.units

        space_time_result = SpaceTimeConvertor.convert(
            self,
            data, 
            from_spatial, 
            to_spatial, 
            from_temporal, 
            to_temporal)
        
        unit_result = UnitConvertor.convert(
            self,
            space_time_result,
            from_unit,
            to_unit)
        
        return unit_result

class ConvertDemandToSupply(SectorModel):
    """Converts energy demand data to energy supply
    """
    def initialise(self, initial_conditions):
        pass

    def simulate(self, data_handle):

        convertor = InputOutputConvertor()

        for input_name, model_input in self.inputs.items():
            self.logger.debug("Model input: %s", model_input)
            model_output = self.outputs[input_name]
            results = convertor.convert_data(data_handle,
                                             model_input,
                                             model_output)
            
            data_handle.set_results(input_name, results)

    def extract_obj(arg):
        pass