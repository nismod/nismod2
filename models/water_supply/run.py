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
        pass

    def simulate(self, data_handle):
        """Runs the water supply model.

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        """

        now = data_handle.current_timestep

        model_dir = os.path.dirname(os.path.realpath(__file__))
        exe_dir = os.path.join(model_dir, 'exe')
        nodal_dir = os.path.join(model_dir, 'nodal')

        # This is the executable itself that requires a sysfile and a nodal file
        wathnet = os.path.join(exe_dir, 'w5_console.exe')
        assert(os.path.isfile(wathnet))

        # This is the national model file, which must be edited to specify which days are simulated
        sysfile = os.path.join(exe_dir, 'National_Model.wat')
        assert(os.path.isfile(sysfile))

        sysfile = self.inject_simulation_days(sysfile, now)
        assert(os.path.isfile(sysfile))

        # This is the nodal file which is generated from various static data files
        nodal_file = self.prepare_nodal(nodal_dir, now)
        assert(os.path.isfile(nodal_file))        

        subprocess.call([
            wathnet,
            '-sysfile={}'.format(sysfile),
            '-nodalfile={}'.format(nodal_file),
            '-output=RA',
        ])

        # Output will be the name of the sysfile (modified_model.wat), without the .wat extension
        # and with (for instance) '_arcFlow.csv' added.
        #   e.g. `modified_model_arcFlow.csv`        
        arc_flows = sysfile.replace('.wat', '_arcFlow.csv')
        assert(os.path.isfile(arc_flows))

        res_vols = sysfile.replace('.wat', '_reservoirEndVolume.csv')
        assert (os.path.isfile(res_vols))

        arc_flows_df = pd.read_csv(
            arc_flows,
            sep=',',
            skiprows=1,  # Row at top called 'Arc flow'
            usecols=lambda col: col.lower() not in ['replicate', 'day', 'year'],
        )

        res_vols_df = pd.read_csv(
            res_vols,
            sep=',',
            skiprows=1,  # Row at top called 'Reservoir end volume'
            usecols=lambda col: col.lower() not in ['replicate', 'day', 'year'],
        )

        data_handle.set_results('water_supply_arc_flows', arc_flows_df.values)
        data_handle.set_results('water_supply_reservoir_end_volumes', res_vols_df.values)

    @staticmethod
    def prepare_nodal(nodal_dir, year_now):
        """Generates the nodal file necessary for the Wathnet model run.

        Arguments
        ---------
        nodal_dir : str
            Path to the directory containing the necessary files for preparing the nodal file.
        
        year_now: int
            The year to be simulated

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

        borehole_file = os.path.join(nodal_dir, 'borehole_forcing_1974_to_2015.csv')
        assert (os.path.isfile(borehole_file))

        nonpublic_file = os.path.join(nodal_dir, 'cams_mean_daily_returns.csv')
        assert (os.path.isfile(nonpublic_file))

        missing_data_file = os.path.join(nodal_dir, 'missing_data.csv')
        assert (os.path.isfile(missing_data_file))

        output_file = os.path.join(nodal_dir, 'wathnet.nodal')

        subprocess.call([
            sys.executable, prepare_nodal,
            '--FlowFile', flow_file,
            '--DemandFile', demand_file,
            '--CatchmentFile', catchment_file,
            '--BoerholeForcingFile', borehole_file,
            '--NonpublicFile', nonpublic_file,
            '--MissingDataFile', missing_data_file,
            '--OutputFile', output_file,
            '--Year', str(year_now),
        ])

        assert(os.path.isfile(output_file))
        return output_file
    
    @staticmethod
    def inject_simulation_days(sysfile, year_now):
        """Injects the current year into the sysfile so that the current year is simulated.

        Arguments
        ---------
        sysfile : str
            Path to the sysfile ('National_Model.wat')
        
        year_now: int
            The year to be simulated
        """

        modified_sysfile = os.path.join(os.path.dirname(sysfile), 'modified_model.wat')

        # This is the unique line directly before the lines we need to edit
        # We should hit this exactly once, which we use to test that nothing has gone wrong
        sentinel_line = '! Run options'
        sentinel_lines_hit = 0

        # String that we want to edit in place
        new_string = '   {}\n  {}\n   {}\n  {}\n'.format('1', str(year_now), '365', str(year_now))

        with open(modified_sysfile, 'w') as new_file:
            with open(sysfile, 'r') as old_file:

                # Write every line from the old file directly into the new file
                for line in old_file:
                    new_file.write(line)
                    
                    # If we see the sentinel, skip 4 lines in the old file and
                    # write the replacement string out instead to the new file
                    if sentinel_line in line:

                        old_file.readline()
                        old_file.readline()
                        old_file.readline()
                        old_file.readline()

                        sentinel_lines_hit += 1
                        new_file.write(new_string)
        
        assert(sentinel_lines_hit == 1)

        return modified_sysfile
