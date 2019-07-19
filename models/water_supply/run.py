"""Water supply model
"""
import os
import subprocess
import sys

import numpy as np
import pandas as pd

from smif.model.sector_model import SectorModel
from smif.data_layer import DataArray


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

        timesteps = data_handle.timesteps
        consecutive_timesteps = tuple(range(timesteps[0], 1 + timesteps[-1]))

        if timesteps != consecutive_timesteps:
            raise ValueError(
                'Water supply requires timesteps to be consecutive years.'
                ' Instead, timesteps are: {}'.format(timesteps)
            )

    def simulate(self, data_handle):
        """Runs the water supply model.

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            A data structure containing all parameters and model inputs defined in
            the smif configuration by name

        """

        now = 1999  # Hack, as some data still only exists for old years. # data_handle.current_timestep

        # Check reservoir data:
        if data_handle.current_timestep == data_handle.base_timestep:
            reservoir_levels = data_handle.get_data('reservoir_levels')
        else:
            reservoir_levels = data_handle.get_previous_timestep_data('reservoir_levels')

        model_dir = os.path.dirname(os.path.realpath(__file__))
        exe_dir = os.path.join(model_dir, 'exe')
        nodal_dir = os.path.join(model_dir, 'nodal')

        # This is the executable itself that requires a sysfile and a nodal file
        wathnet = os.path.join(exe_dir, 'w5_console.exe')
        assert(os.path.isfile(wathnet)), "Expected to find water supply WATHNET executable at {}".format(wathnet)

        # This is the national model file, which must be edited to specify which days are simulated
        sysfile = os.path.join(exe_dir, 'National_Model.wat')
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        sysfile = self.inject_simulation_days(sysfile, now)
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        # This is the nodal file which is generated from various static data files
        nodal_file = self.prepare_nodal(data_handle, nodal_dir, now)
        assert(os.path.isfile(nodal_file))

        subprocess.call([
            wathnet,
            '-sysfile={}'.format(sysfile),
            '-nodalfile={}'.format(nodal_file),
            '-output=RAGDS',
        ])

        # Output will be the name of the sysfile (modified_model.wat), without the .wat extension
        # and with (for instance) '_arcFlow.csv' added.
        #   e.g. `modified_model_arcFlow.csv`
        arc_flows = sysfile.replace('.wat', '_arcFlow.csv')
        assert(os.path.isfile(arc_flows)), "Expected to find water supply arc flow results at {}".format(arc_flows)
        data_handle.set_results(
            'water_supply_arc_flows',
            self.extract_wathnet_output(output_file=arc_flows, spec=self.outputs['water_supply_arc_flows'])
        )

        res_vols = sysfile.replace('.wat', '_reservoirEndVolume.csv')
        assert (os.path.isfile(res_vols)), "Expected to find water supply reservoir results at {}".format(res_vols)
        data_handle.set_results(
            'water_supply_reservoir_daily_volumes',
            self.extract_wathnet_output(output_file=res_vols, spec=self.outputs['water_supply_reservoir_daily_volumes'])
        )

        global_vars = sysfile.replace('.wat', '_globalPlotVars_selected.csv')
        assert (os.path.isfile(global_vars)), "Expected to find water supply global variables at {}".format(global_vars)
        data_handle.set_results(
            'water_supply_global_variables',
            self.extract_wathnet_output(output_file=global_vars, spec=self.outputs['water_supply_global_variables'])
        )

        req_demand = sysfile.replace('.wat', '_requestedDemand.csv')
        assert (os.path.isfile(req_demand)), "Expected to find water supply requested demands at {}".format(req_demand)

        shortfalls = sysfile.replace('.wat', '_demandShortfall.csv')
        assert (os.path.isfile(shortfalls)), "Expected to find water supply requested demands at {}".format(shortfalls)

        # Last row in reservoir volumes is for day 365, which is an input for the next timestep
        data_handle.set_results(
            'reservoir_levels',
            data_handle.get_results('water_supply_reservoir_daily_volumes').data[-1]
        )

    def prepare_nodal(self, data_handle, nodal_dir, year_now):
        """Generates the nodal file necessary for the Wathnet model run.

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            A data structure containing all parameters and model inputs defined in
            the smif configuration by name

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
        assert (os.path.isfile(prepare_nodal)), "Expected to find prepare_nodal script at {}".format(prepare_nodal)

        flow_file = os.path.join(nodal_dir, 'National_WRSM_NatModel_logNSE_obs_11018_1.txt')
        assert (os.path.isfile(flow_file)), "Expected to find water supply flows file at {}".format(flow_file)

        demand_file = os.path.join(nodal_dir, '001_daily.csv')
        assert (os.path.isfile(demand_file)), "Expected to find water supply demand file at {}".format(demand_file)

        catchment_file = os.path.join(nodal_dir, 'CatchmentIndex.csv')
        assert (os.path.isfile(catchment_file)), "Expected to find water supply catchment file at {}".format(catchment_file)

        borehole_file = os.path.join(nodal_dir, 'borehole_forcing_1974_to_2015.csv')
        assert (os.path.isfile(borehole_file)), "Expected to find water supply borehole data at {}".format(borehole_file)

        public_file = os.path.join(nodal_dir, 'WRZ_DI_DO.csv')
        assert (os.path.isfile(public_file)), "Expected to find water supply public data at {}".format(public_file)
        public_file = self.inject_new_demands(public_file, data_handle.get_data('water_demand'))

        nonpublic_file = os.path.join(nodal_dir, 'cams_mean_daily_returns.csv')
        assert (os.path.isfile(nonpublic_file)), "Expected to find water supply nonpublic data at {}".format(nonpublic_file)

        missing_data_file = os.path.join(nodal_dir, 'missing_data.csv')
        assert (os.path.isfile(missing_data_file)), "Expected to find water supply missing data at {}".format(missing_data_file)

        demand_profiles_file = os.path.join(nodal_dir, '2019_June_06_Demand_Profiles.csv')
        assert (os.path.isfile(demand_profiles_file)), "Expected to find water supply missing data at {}".format(demand_profiles_file)

        dynatop_file = os.path.join(nodal_dir, 'master_dynatop_points.csv')
        assert (os.path.isfile(dynatop_file)), "Expected to find water supply missing data at {}".format(dynatop_file)

        output_file = os.path.join(nodal_dir, 'wathnet.nodal')

        subprocess.call([
            sys.executable, prepare_nodal,
            '--FlowFile', flow_file,
            '--DemandFile', demand_file,
            '--CatchmentFile', catchment_file,
            '--BoreholeForcingFile', borehole_file,
            '--PublicFile', public_file,
            '--NonpublicFile', nonpublic_file,
            '--MissingDataFile', missing_data_file,
            '--DemandProfilesFile', demand_profiles_file,
            '--DynatopFile', dynatop_file,
            '--OutputFile', output_file,
            '--Year', str(year_now),
        ])

        assert(os.path.isfile(output_file)), "Expected to find WATHNET nodal file at {}".format(output_file)
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

    @staticmethod
    def inject_new_demands(public_file, demand_data):
        """Injects the water demand data calculated by the water demand model into the public file.

        Arguments
        ---------
        public_file : str
            Path to the public file ('WRZ_DI_DO.csv')

        demand_data: smif.data_layer.DataArray
            The demand data to inject into the public file
        """

        assert public_file.endswith('.csv'), "Expected public file to be a csv file"

        new_file = public_file + ".NEW_DEMANDS"

        # Read the existing CSV using Pandas, and as a sanity check assert it is written
        # back out identically (to ensure nothing has gone wrong reading the file)
        public_df = pd.read_csv(
            public_file,
            sep=',',
        )

        coord_names_from_smif = np.array([x['name'] for x in demand_data.dim_coords('water_resource_zones').elements])
        coord_names_in_csv = np.array(public_df['WRZ Name'])

        if len(coord_names_from_smif) != len(coord_names_in_csv):
            raise ValueError(
                'Expected the calculated water demand from water demand model to have to have the same coordinates as'
                ' the "WRZ Name" column in the public file (WRZ_DI_DO.csv). But, they have different lengths ({} and'
                ' {})'.format(len(coord_names_from_smif), len(coord_names_in_csv))
            )

        for x, y in zip(coord_names_from_smif, coord_names_in_csv):
            if x != y and 'Nottinghamshire' not in x:  # hack, as Nottinghamshire.1 and Nottinghamshire.2 from smif
                raise ValueError(
                    'Expected the calculated water demand from water demand model to have to have the same coordinates'
                    ' as the "WRZ Name" column in the public file (WRZ_DI_DO.csv). Instead, found non-matching'
                    ' coordinates ({} <=> {})'.format(x, y)
                )

        # Inject the new demand data, and create a new CSV file
        public_df['Distribution Input'] = demand_data.data
        assert np.array_equal(demand_data.data, public_df['Distribution Input'])

        public_df.to_csv(path_or_buf=new_file, sep=',', header=True, index=False)
        assert os.path.isfile(new_file)

        return new_file

    @staticmethod
    def extract_wathnet_output(output_file, spec):
        """Injects the water demand data calculated by the water demand model into the public file.

        Arguments
        ---------
        output_file : str
            Path to the output file
        spec : smif.metadata.Spec
            The expected spec for verifying integrity of output

        Returns
        =======
        data : numpy.ndarray
            The data from the output file
        """

        # Read the output file and melt it on the column "Day"
        output_df = pd.read_csv(
            output_file,
            sep=',',
            skiprows=1,  # All wathnet output contains a single row of description
            usecols=lambda col: col.lower() not in ['replicate', 'year'],
        ).melt(id_vars=['Day'])

        # Rename the columns to match the spec object
        output_df.rename(
            inplace=True,
            columns={
                'Day': spec.dims[0],
                'variable': spec.dims[1],
                'value': spec.name,
            }
        )

        # Returning via DataArray.from_df will check that the data matches the spec as expected
        return DataArray.from_df(spec=spec, dataframe=output_df).data
