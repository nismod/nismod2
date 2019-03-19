"""Water supply model
"""
import configparser
import os
import subprocess

import numpy as np
import pandas as pd

from smif.model.sector_model import SectorModel


class WaterWrapper(SectorModel):
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
        # This might have to handle the prepare_nodal that is currently done during installation
        pass

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Returns
        =======
        et_module_out : dict
            Outputs of et_module
        """

        base_path = os.path.dirname(os.path.abspath(__file__))
        config_file_path = os.path.join(base_path, 'wrapperconfig.ini')

        config = configparser.ConfigParser()
        config.read(config_file_path)

        data_dir = '/vagrant/data/water_supply'

        wathnet_exe = 'w5_console.exe'
        national_model = 'National_Model.wat'
        nodal_file = 'wathnet.nodal'

        wathnet = os.path.join(data_dir, wathnet_exe)
        assert(os.path.isfile(wathnet))

        sysfile = os.path.join(data_dir, national_model)
        assert(os.path.isfile(sysfile))

        nodalfile = os.path.join(data_dir, nodal_file)
        assert(os.path.isfile(nodalfile))

        subprocess.call([
            wathnet,
            '-sysfile={}'.format(sysfile),
            '-nodalfile={}'.format(nodalfile),
            '-output=RA',
        ])

        arc_flows = os.path.join(data_dir, 'National_Model_arcFlow.csv')
        assert(os.path.isfile(arc_flows))

        res_vols = os.path.join(data_dir, 'National_Model_reservoirEndVolume.csv')
        assert (os.path.isfile(res_vols))

        arc_flows_df = pd.read_csv(
            arc_flows,
            sep=',',
            skiprows=1,  # Row at top called 'Arc flow'
            usecols=lambda col: True  # might want to subset columns
        )

        res_vols_df = pd.read_csv(
            res_vols,
            sep=',',
            skiprows=1,  # Row at top called 'Reservoir end volume'
            usecols=lambda col: True  # might want to subset columns
        )

        print(arc_flows_df)
        print(res_vols_df)

        # Need to decide what to do here...

        # data_handle.set_results('v2g_g2v_capacity', actual_v2g_capacity)


if __name__ == '__main__':
    ww = WaterWrapper('sdfg')
    ww.simulate({})
