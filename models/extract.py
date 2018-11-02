"""Utility model wrapper to extract a subset of coordinates from a dimension

For example, extracting four LADs from an input which covers all 391 LADs in the UK:
- input with dimension 'lad_uk_2016', coordinate names 'E06000001', 'E06000002', ...
- output with dimension 'lad_southampton', coordinate names 'E06000045', 'E07000086',
  'E07000091' and 'E06000046'
"""
from smif.data_layer.data_array import DataArray as SmifDataArray
from smif.exception import SmifException
from smif.model import SectorModel
from xarray import DataArray as XDataArray

class FilterAdaptor(SectorModel):
    """Adaptor to filter input-output pairs
    """
    def simulate(self, data):
        for input_name, model_input in self.inputs.items():
            try:
                model_output = self.outputs[input_name]
            except KeyError:
                msg = "Output '{}' not found to match input '{}' in model '{}'".format(
                    input_name, model_input, self.name)
                raise SmifException(msg)

            results = self.filter(data, model_input, model_output)
            data.set_results(input_name, results)

    def filter(self, data_handle, input_spec, output_spec):
        """Filter an input dataset

        Given a pair of input-output specs which differ in exactly one dimension, pick the
        subset of coordinates from the input which are needed in the output.
        """
        input_dim, input_coords = self._pick_dim_coords(input_spec, output_spec)
        output_dim, output_coords = self._pick_dim_coords(output_spec, input_spec)
        msg = "Expected output coords to be a subset of input coords in {}:{}".format(
            self.name, input_spec.name)
        assert output_coords.issubset(input_coords), msg

        input_df = data_handle.get_data(input_spec.name).as_df().reset_index()
        output_df = input_df[
            input_df[input_dim].isin(output_coords)
        ]
        output_df = output_df.rename(columns={input_dim: output_dim, 0:output_spec.name})
        print(output_df)
        # go from pandas.Series to smif.DataArray (tidy with MultiIndex -> compact ndarray)
        # may refactor/rework with helper methods on smif.DataArray
        output_df.set_index(output_spec.dims, inplace=True)
        output_ds = output_df.iloc[:, 0]
        output_ds.name = output_spec.name
        output_xr = XDataArray.from_series(output_ds)
        data = output_xr.data
        print(data)
        return data

    def _pick_dim_coords(self, a_spec, b_spec):
        dims = set(a_spec.dims) - set(b_spec.dims)
        assert len(dims) == 1, "Expected one dimension to differ in {}:{}".format(
            self.name, a_spec.name)
        dim = dims.pop()
        coords = a_spec.dim_coords(dim)
        coords_names = frozenset(coords.ids)
        return dim, coords_names
