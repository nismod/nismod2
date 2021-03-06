"""Water supply model
"""
import os
import re
import shutil
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

        base_dir = os.path.dirname(os.path.realpath(__file__))
        model_dir = self._get_model_dir(data_handle)

        try:
            os.mkdir(model_dir)
        except FileExistsError:
            pass

        base_exe_dir = os.path.join(base_dir, 'exe')
        model_exe_dir = os.path.join(model_dir, 'exe')
        try:
            shutil.copytree(base_exe_dir, model_exe_dir)
        except FileExistsError:
            pass

        base_nodal_dir = os.path.join(base_dir, 'nodal')
        model_nodal_dir = os.path.join(model_dir, 'nodal')
        try:
            shutil.copytree(base_nodal_dir, model_nodal_dir)
        except FileExistsError:
            pass


    def _get_model_dir(self, data_handle):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            os.path.basename(data_handle._modelrun_name))

    def simulate(self, data_handle):
        """Runs the water supply model.

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            A data structure containing all parameters and model inputs defined in
            the smif configuration by name

        """

        # Check reservoir data:
        if data_handle.current_timestep == data_handle.base_timestep:
            reservoir_levels = data_handle.get_data('reservoir_levels')
        else:
            reservoir_levels = data_handle.get_previous_timestep_data('reservoir_levels')

        model_dir = self._get_model_dir(data_handle)
        exe_dir = os.path.join(model_dir, 'exe')
        nodal_dir = os.path.join(model_dir, 'nodal')

        # This is the executable itself that requires a sysfile and a nodal file
        wathnet = os.path.join(exe_dir, 'w5_console.exe')
        assert(os.path.isfile(wathnet)), "Expected to find water supply WATHNET executable at {}".format(wathnet)

        # This is the national model file, which must be edited in various ways:
        sysfile = os.path.join(exe_dir, 'National_Model.wat')
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        # Inject the current simulation period (current timestep)
        sysfile = self.inject_simulation_days(sysfile, data_handle.current_timestep)
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        # Inject the reservoir levels from the previous timestep
        sysfile = self.inject_reservoir_levels(sysfile, reservoir_levels)
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        # Set intervention
        sysfile = self.set_interventions(sysfile, data_handle.get_current_interventions())
        assert(os.path.isfile(sysfile)), "Expected to find water supply sysfile at {}".format(sysfile)

        # This is the nodal file which is generated from various static data files
        nodal_file = self.prepare_nodal(data_handle, nodal_dir)
        assert(os.path.isfile(nodal_file))

        subprocess.call([
            wathnet,
            '-sysfile={}'.format(sysfile),
            '-nodalfile={}'.format(nodal_file),
            '-output=RGDS',
            '-save',  # enable to allow debugging in WATHNET GUI with data in line
        ])

        # Output will be the name of the sysfile (modified_model.wat), without the .wat extension
        # and with (for instance) '_reservoirEndVolume.csv' added.
        #   e.g. `modified_model_reservoirEndVolume.csv`
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
        data_handle.set_results(
            'water_supply_requested_demand',
            self.extract_wathnet_output(output_file=req_demand, spec=self.outputs['water_supply_requested_demand'])
        )

        shortfalls = sysfile.replace('.wat', '_demandShortfall.csv')
        assert (os.path.isfile(shortfalls)), "Expected to find water supply requested demands at {}".format(shortfalls)
        data_handle.set_results(
            'water_supply_shortfall',
            self.extract_wathnet_output(output_file=shortfalls, spec=self.outputs['water_supply_shortfall'])
        )

        # Last row in reservoir volumes is for day 365, which is an input for the next timestep
        data_handle.set_results(
            'reservoir_levels',
            data_handle.get_results('water_supply_reservoir_daily_volumes').data[-1]
        )

    @staticmethod
    def prepare_nodal(data_handle, nodal_dir):
        """Generates the nodal file necessary for the Wathnet model run. The script to prepare the nodal file requires
        a number of csv files as parameters. Some of these data come via the data_handle as either parameters or
        scenario data, and some are installed with the water_supply model. Those that come via the data_handle must be
        reformatted into a square format expected by the prepare_nodal script.

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            A data structure containing all parameters and model inputs defined in
            the smif configuration by name

        nodal_dir : str
            Path to the directory containing the necessary files for preparing the nodal file.

        Returns
        =======
        output_file : str
            The path to the generated nodal file
        """

        # Find the prepare nodal script
        prepare_nodal = os.path.join(nodal_dir, 'prepare_nodal.py')
        assert (os.path.isfile(prepare_nodal)), "Expected to find prepare_nodal script at {}".format(prepare_nodal)

        #######################################
        # Data from data handle as parameters #
        #######################################

        # The nonpublic water demand
        nonpublic_df = data_handle.get_parameter('nonpublic_water_demand').as_df().reset_index().pivot(
            index='water_supply/cams_names',
            columns='water_supply/nonpublic_use_codes',
            values='nonpublic_water_demand'
        ).reset_index()

        nonpublic_df.rename(
            inplace=True,
            columns={
                'water_supply/cams_names': 'cams_name',
            }
        )

        nonpublic_file = os.path.join(nodal_dir, 'nonpublic_water_demand.csv')
        nonpublic_df.to_csv(nonpublic_file, index=False)
        assert os.path.isfile(nonpublic_file),\
            "Expected to find water supply nonpublic data at {}".format(nonpublic_file)

        # The demand profiles
        demand_df = data_handle.get_parameter('demand_profiles').as_df().reset_index().pivot(
            index='water_supply/days_into_year',
            columns='water_supply/demand_profile_zones',
            values='demand_profiles'
        ).reset_index()

        demand_df.rename(
            inplace=True,
            columns={
                'water_supply/days_into_year': 'Day',
            }
        )

        demand_profiles_file = os.path.join(nodal_dir, 'demand_profiles.csv')
        demand_df.to_csv(demand_profiles_file, index=False)
        assert os.path.isfile(demand_profiles_file),\
            "Expected to find water supply missing data at {}".format(demand_profiles_file)

        ##########################################
        # Data from data handle as scenario data #
        ##########################################

        # The flows data
        flows_data = data_handle.get_data('flows_data', data_handle.current_timestep)

        flows_df = flows_data.as_df().reset_index().pivot(
            index='water_supply/days_into_year',
            columns='water_supply/flow_file_column_names',
            values='flows_data'
        ).reset_index()

        col_month = np.array([x['month'] for x in flows_data.dim_coords('water_supply/days_into_year').elements])
        col_day = np.array([x['day'] for x in flows_data.dim_coords('water_supply/days_into_year').elements])
        col_year = np.array([data_handle.current_timestep] * len(col_month))

        flows_df.insert(0, 'DAY', col_day)
        flows_df.insert(0, 'MONTH', col_month)
        flows_df.insert(0, 'YEAR', col_year)
        flows_df.drop(columns=['water_supply/days_into_year'], inplace=True)

        flows_file = os.path.join(nodal_dir, 'flows_file.csv')
        flows_df.to_csv(flows_file, index=False, na_rep='NaN', sep='\t')
        assert os.path.isfile(flows_file), \
            "Expected to find water supply flows data at {}".format(flows_file)

        # The irrigations demand data
        irrigations_data = data_handle.get_data('irrigations_data', data_handle.current_timestep)

        irrigations_df = irrigations_data.as_df()

        unstacked_df = irrigations_df.unstack(level=-1)
        unstacked_df.columns = unstacked_df.columns.get_level_values(1)
        unstacked_df.reset_index(inplace=True)
        unstacked_df.sort_values(
            by=['water_supply/irrigations_cams_names', 'water_supply/days_into_year'],
            inplace=True
        )

        col_date = np.array([
            x['day_month'] + str(data_handle.current_timestep) for x in irrigations_data.dim_coords(
                'water_supply/days_into_year'
            ).elements
        ] * len(unstacked_df['water_supply/irrigations_cams_names'].unique()))

        unstacked_df.insert(2, 'date', col_date)
        unstacked_df.drop(columns=['water_supply/days_into_year'], inplace=True)

        unstacked_df.rename(
            inplace=True,
            columns={
                'water_supply/irrigations_cams_names': 'cams_name',
            }
        )

        irrigations_file = os.path.join(nodal_dir, 'irrigations_file.csv')
        unstacked_df.to_csv(irrigations_file, index=False, na_rep='NaN', sep=',')
        assert os.path.isfile(irrigations_file), \
            "Expected to find water supply irrigations data at {}".format(irrigations_file)

        # The borehole data
        borehole_data = data_handle.get_data('borehole_data', data_handle.current_timestep)
        borehole_df = borehole_data.as_df().reset_index().pivot(
            index='water_supply/months_into_year',
            columns='water_supply/borehole_names',
            values='borehole_data'
        ).reset_index()

        borehole_df.rename(
            inplace=True,
            columns={
                'water_supply/months_into_year': 'Month',
            }
        )

        col_year = [data_handle.current_timestep] * 12
        borehole_df.insert(1, 'Year', col_year)

        # Reorder the columns as expected by the prepare nodal script
        borehole_names = [x['name'] for x in borehole_data.dim_coords('water_supply/borehole_names').elements]
        col_order = ['Month', 'Year'] + borehole_names
        borehole_df = borehole_df[col_order]

        borehole_file = os.path.join(nodal_dir, 'borehole_file.csv')
        borehole_df.to_csv(borehole_file, index=False, na_rep='NaN', sep=',')
        assert os.path.isfile(borehole_file), \
            "Expected to find water supply borehole data at {}".format(borehole_file)

        ####################################
        # Data installed with water_supply #
        ####################################

        catchment_file = os.path.join(nodal_dir, 'CatchmentIndex.csv')
        assert (os.path.isfile(catchment_file)),\
            "Expected to find water supply catchment file at {}".format(catchment_file)

        missing_data_file = os.path.join(nodal_dir, 'missing_data.csv')
        assert (os.path.isfile(missing_data_file)),\
            "Expected to find water supply missing data at {}".format(missing_data_file)

        public_file = os.path.join(nodal_dir, 'WRZ_DI_DO.csv')
        assert (os.path.isfile(public_file)),\
            "Expected to find water supply public data at {}".format(public_file)
        public_file = WaterWrapper.inject_new_demands(public_file, data_handle.get_data('water_demand'))

        dynatop_file = os.path.join(nodal_dir, 'master_dynatop_points.csv')
        assert (os.path.isfile(dynatop_file)),\
            "Expected to find water supply missing data at {}".format(dynatop_file)

        ###################################
        # Generate the wathnet nodal file #
        ###################################

        output_file = os.path.join(nodal_dir, 'wathnet.nodal')

        subprocess.call([
            sys.executable, prepare_nodal,
            '--FlowFile', flows_file,
            '--DemandFile', irrigations_file,
            '--CatchmentFile', catchment_file,
            '--BoreholeForcingFile', borehole_file,
            '--PublicFile', public_file,
            '--NonpublicFile', nonpublic_file,
            '--MissingDataFile', missing_data_file,
            '--DemandProfilesFile', demand_profiles_file,
            '--DynatopFile', dynatop_file,
            '--OutputFile', output_file,
            '--Year', str(data_handle.current_timestep),
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

        Returns
        =======
        sysfile : str
            The name of the new wathnet sysfile
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
    def set_interventions(sysfile, interventions):
        """Set ITRC intervention
        """
        interventions = list(interventions.values())

        msg = "Expected at most one intervention for water supply, got {}"
        assert len(interventions) <= 1, msg.format(interventions)

        if interventions and 'option_number' in interventions[0]:
            option_number = interventions[0]['option_number']
        else:
            option_number = 0

        # Option Number sets the value of itrco in the National_Model.wat file, with effects
        # as defined within the file:
        # itrco = 0 - no options;
        # itrco = 1 - severn thames transfer;
        # itrco = 2 - trent to rutland transfer;
        # itrco = 3 - s lincs reservoir;
        # itrco = 4 - abingdon storage;
        # itrco = 5 - beckton reuse;

        # open file
        with open(sysfile, 'r') as fh:
            original_text = fh.read()

        # modify
        new_text = original_text.replace("itrco = 0;", "itrco = {};".format(option_number))

        # save modified file
        new_sysfile = sysfile.replace('.wat', '_with_intervention.wat')
        with open(new_sysfile, 'w') as fh:
            fh.write(new_text)

        return new_sysfile

    @staticmethod
    def inject_reservoir_levels(sysfile, reservoir_levels):
        """Injects reservoir levels passed in through the smif data handle to the Wathnet sysfile.

        Arguments
        ---------
        sysfile : str
            Path to the sysfile ('National_Model.wat')

        reservoir_levels: smif.data_layer.DataArray
            The reservoir levels to inject into the sysfile

        Returns
        =======
        sysfile : str
            The name of the new wathnet sysfile
        """

        res_names = np.array([x['name'] for x in reservoir_levels.dim_coords('water_supply/reservoir_names').elements])
        res_vols = reservoir_levels.data

        node_num_dict = WaterWrapper.get_reservoir_node_numbers(sysfile, res_names)

        with open(sysfile, 'r') as my_f:
            original_file = my_f.read()

        # A string not in the original file, for keeping track of the number of successful substitutions
        sentinel = r'#~@@~#'
        assert sentinel not in original_file

        # Perform the required substitutions
        for res_name, res_vol in zip(res_names, res_vols):

            # Pattern (<...>)\d+ where the group (<...>) matches based on the node number and reservoir name
            # and the \d+ is the number that is to be replaced by the substitution
            regex_pattern = r'(\n\s+{}\s+{}\s+1.*\n.*\n.*9999999\s+\d+\s+)\d+'.format(
                node_num_dict[res_name], re.escape(res_name)
            )

            # Keep the first group (\g<1>) unchanged, then add the correct volume and the sentinel
            original_file = re.sub(
                pattern=regex_pattern,
                repl=r'\g<1>{}{}'.format(int(res_vol), sentinel),
                string=original_file,
                count=1
            )

        # The number of occurrences of the sentinel should equal the number of reservoirs.
        # If not, at least one replacement did not occur as expected.
        num_sentinels = original_file.count(sentinel)
        assert num_sentinels == len(res_names), \
            'Only {}/{} reservoir levels were replaced. Something went wrong!'.format(num_sentinels, len(res_names))

        # Finally, write out a new file, removing the sentinels
        new_filename = sysfile.replace('.wat', '_with_res_vols.wat')

        with open(new_filename, 'w') as my_f:
            my_f.write(original_file.replace(sentinel, ''))

        return new_filename

    @staticmethod
    def get_reservoir_node_numbers(sysfile, reservoir_names):
        """Identifies node numbers corresponding to reservoir names from the wathnet sysfile.

        Arguments
        ---------
        sysfile : str
            Path to the sysfile ('National_Model.wat')

        reservoir_names: List[str]
            List of reservoir names

        Returns
        =======
        node_num_dict : dict
            Mapping from reservoir name to integer node number
        """

        # For efficiency, we pull out the relevant part of the sysfile,
        # between '! Node data' and '!-------------------------------'
        with open(sysfile, 'r') as my_file:
            line = ''
            while '! Node data' not in line:
                line = my_file.readline()

            node_data_lines = [line]

            while '!--------------------------------------------------------' not in line:
                line = my_file.readline()
                node_data_lines.append(line.strip())

        node_data = '\n'.join(node_data_lines)

        # Populate the dictionary mapping reservoir name to node number
        node_num_dict = {}
        for res_name in reservoir_names:

            # We're looking for <node_num> <res name>\n <node_type>
            # where <node_type> is always 1 for reservoirs
            regex_pattern = r'\n(\d+)\s+{}\s+1\s+'.format(re.escape(res_name))
            m = re.search(regex_pattern, node_data)

            assert m is not None, 'Expected to find a match for {} in {}'.format(regex_pattern, sysfile)

            node_num_dict[res_name] = m.group(1)

        return node_num_dict

    @staticmethod
    def inject_new_demands(public_file, demand_data):
        """Injects the water demand data calculated by the water demand model into the public file.

        Arguments
        ---------
        public_file : str
            Path to the public file ('WRZ_DI_DO.csv')

        demand_data: smif.data_layer.DataArray
            The demand data to inject into the public file

        Returns
        =======
        new_public_file : str
            The name of the new public demands file
        """

        assert public_file.endswith('.csv'), "Expected public file to be a csv file"

        new_public_file = public_file + ".NEW_DEMANDS"

        # Read template file
        public_df = pd.read_csv(
            public_file,
            sep=',',
        )

        # Merge, replacing values for 'Distribution Input'
        smif_demand_df = demand_data.as_df().reset_index()

        public_df = public_df.merge(
            smif_demand_df,
            left_on='WRZ Name',
            right_on='water_resource_zones',
            validate='one_to_one'
        ).drop(
            ['Distribution Input', 'water_resource_zones'], axis=1
        ).rename(columns={
            'water_demand': 'Distribution Input'
        })

        public_df.to_csv(new_public_file, index=False)
        assert os.path.isfile(new_public_file)

        return new_public_file

    @staticmethod
    def extract_wathnet_output(output_file, spec):
        """Given a Wathnet output file, extracts the data smif is expecting, verifying the spec matches.

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
