"""This adapter aggregates all inputs and writes the aggregate
values to each output
"""
import numpy as np
from smif.model import SectorModel


class AggregateInputs(SectorModel):
    """An Adapter to aggregate all inputs

    Outputs the same aggregate to each output.
    """
    def simulate(self, data_handle):
        """Aggregates inputs to output
        """
        inputs = []
        for input_name in self.inputs.keys():
            self.logger.debug("Model input: %s", input_name)
            inputs.append(data_handle.get_data(input_name).as_ndarray())

        data_array = np.array(inputs)
        aggregate_data = np.add.reduce(data_array, axis=0)

        for output_name in self.outputs.keys():
            data_handle.set_results(output_name, aggregate_data)
