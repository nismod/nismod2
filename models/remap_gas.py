"""This adapter aggregates all inputs and writes the aggregate
values to each output
"""
import os
from csv import DictReader

import numpy as np
from smif.model.sector_model import SectorModel

def read_gas_remap(file_name):
    with open(file_name, 'r') as load_map:
        reader = DictReader(load_map)
        gas_remap = [{'node': int(x['Node']),
                      'eh': int(x['EH_Conn_Num']),
                      'share': x['Load Share'] } for x in reader]

        mapper = {}
        for row in gas_remap:
            if row['eh'] in mapper.keys():
                mapper[int(row['eh'])].update({row['node']: row['share']})
            else:
                mapper[int(row['eh'])] = {row['node']: row['share']}

        return mapper

def remap_gas(data, remap_filename):
    """Remaps `data` using the mapping file `remap_filename`

    Builds a coefficient matrix and reshapes the regions of the `data`

    Returns
    -------
    reshaped_data : numpy.ndarray
        An array of data with dimensions regions-by-intervals
    gas_nodes : list
        A list of the gas node region names
    """

    mapper = read_gas_remap(remap_filename)

    coefficients = np.zeros((29, 87), dtype=float)
    for hub, gas_nodeshare in mapper.items():
        for gas_node, share in gas_nodeshare.items():
            coefficients[hub - 1, gas_node - 1] = share

    reshaped_data = np.dot(data.T, coefficients).T
    return reshaped_data


class RemapEnergyHubToGasNode(SectorModel):
    """Convert spatial resolution (energy hubs to gas nodes)
    """
    def simulate(self, data_handle):
        """Remaps energy demand from energy hubs to gas nodes
        """
        gasload_eh = data_handle.get_data('gasload').as_ndarray()
        nismod_dir = os.path.join(os.path.dirname(__file__), '..')
        remap_file = os.path.join(
            nismod_dir, 'data', 'energy_supply', 'database_full', '_GasLoadMap.csv')

        gasload_nodes = remap_gas(gasload_eh, remap_file)

        data_handle.set_results('gasload', gasload_nodes)
