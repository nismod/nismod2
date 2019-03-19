"""Water supply model
"""
import os
import subprocess
import sys

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
        """Runs the water supply model.

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        """

        model_dir = os.path.dirname(os.path.realpath(__file__))
        exe_dir = os.path.join(model_dir, 'exe')
        nodal_dir = os.path.join(model_dir, 'nodal')

        wathnet = os.path.join(exe_dir, 'w5_console.exe')
        assert(os.path.isfile(wathnet))

        sysfile = os.path.join(exe_dir, 'National_Model.wat')
        assert(os.path.isfile(sysfile))

        nodal_file = self.prepare_nodal(nodal_dir)
        assert(os.path.isfile(nodal_file))

        subprocess.call([
            wathnet,
            '-sysfile={}'.format(sysfile),
            '-nodalfile={}'.format(nodal_file),
            '-output=RA',
        ])

        arc_flows = os.path.join(exe_dir, 'National_Model_arcFlow.csv')
        assert(os.path.isfile(arc_flows))

        res_vols = os.path.join(exe_dir, 'National_Model_reservoirEndVolume.csv')
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

        # print(arc_flows_df)
        # print(res_vols_df)

        # Need to decide what to do here...

        # data_handle.set_results('v2g_g2v_capacity', actual_v2g_capacity)

    @staticmethod
    def prepare_nodal(nodal_dir):
        """Generates the nodal file necessary for the Wathnet model run.

        Arguments
        ---------
        nodal_dir : str
            Path to the directory containing the necessary files for preparing the nodal file.

        Returns
        =======
        output_file : str
            The path to the generated nodal file
        """

        # Check necessary files exist
        prepare_nodal = os.path.join(nodal_dir, 'prepare_nodal.py')
        print(prepare_nodal)
        assert (os.path.isfile(prepare_nodal))

        flow_file = os.path.join(nodal_dir, 'National_WRSM_NatModel_logNSE_obs_11018_1.txt')
        assert (os.path.isfile(flow_file))

        demand_file = os.path.join(nodal_dir, '001_daily.csv')
        assert (os.path.isfile(demand_file))

        catchment_file = os.path.join(nodal_dir, 'CatchmentIndex.csv')
        assert (os.path.isfile(catchment_file))

        missing_data_file = os.path.join(nodal_dir, 'missing_data.csv')
        assert (os.path.isfile(missing_data_file))

        output_file = os.path.join(nodal_dir, 'wathnet.nodal')

        subprocess.call([
            sys.executable, prepare_nodal,
            '--FlowFile', flow_file,
            '--DemandFile', demand_file,
            '--CatchmentFile', catchment_file,
            '--MissingDataFile', missing_data_file,
            '--OutputFile', output_file,
        ])

        assert(os.path.isfile(output_file))
        return output_file


if __name__ == '__main__':
    ww = WaterWrapper('sdfg')
    ww.simulate({})
