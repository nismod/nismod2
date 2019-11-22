"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
from collections import defaultdict
from shapely.geometry import shape, mapping

from smif.model.sector_model import SectorModel

from energy_demand import wrapper_model
from energy_demand.assumptions import strategy_vars_def, general_assumptions
from energy_demand.main import energy_demand_model
from energy_demand.basic import basic_functions
from energy_demand.read_write import (write_data, read_data, data_loader,
                                      narrative_related)

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)
        self.user_data = {}

    def _assign_array_to_dict(self, array_in, regions):
        """Convert array to dict with same order as region list

        Input
        -----
        array_in : array
            Data array with data like the order of the region list
        regions : list
            List with specific order of regions

        Returns
        -------
        dict_out : dict
            Dictionary of array_in
        """
        dict_out = {}
        for r_idx, region in enumerate(regions):
            dict_out[region] = array_in[r_idx]
        return dict_out

    def _get_mode(self, data_handle):
        """Get constrained or unconstrained mode
        """
        param_raw_series = data_handle.get_parameter('mode').as_df()
        df_raw = self._series_to_df(param_raw_series, 'mode')
        mode = int(df_raw['mode'][0])

        if mode == 1:
            mode_out = True
        if mode == 0:
            mode_out = False
        return mode_out

    def _get_virtual_dw_stock(self, data_handle):
        """Get virtual dwellig stock criteria ( if floor area is read in directly or not)
        """
        param_raw_series = data_handle.get_parameter('virtual_dw_stock').as_df()
        df_raw = self._series_to_df(param_raw_series, 'virtual_dw_stock')
        mode = int(df_raw['virtual_dw_stock'][0])

        if mode == 1:
            mode_out = True
        if mode == 0:
            mode_out = False
        return mode_out

    def _get_working_dir(self):
        """Get path
        """
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def create_folders_rename_folders(config):
        """Create scenario name and get paths

        Arguments
        ---------
        config : dict
            Configuration dictionary containing all the file paths
        """
        path_new_scenario = config['PATHS']['path_new_scenario']

        # ------------------------------
        # Delete previous model results and create result folders
        # ------------------------------
        result_paths = config['PATHS']['path_result_data']
        basic_functions.del_previous_setup(result_paths)
        basic_functions.create_folder(path_new_scenario)

        folders_to_create = [
            os.path.join(result_paths, 'model_run_pop'),
            os.path.join(result_paths, 'validation')]

        for folder in folders_to_create:
            basic_functions.create_folder(folder)

    @staticmethod
    def _get_region_set_name():
        return 'lad_uk_2016'

    @staticmethod
    def _get_base_yr(data_handle):
        return data_handle.timesteps[0]

    @staticmethod
    def _get_simulation_yr(data_handle):
        return data_handle.current_timestep

    @staticmethod
    def _get_simulation_yrs(data_handle):
        return data_handle.timesteps

    @staticmethod
    def _series_to_df(series, name):
        return series.reset_index().rename(columns={0: name})

    @staticmethod
    def centroids_as_features(regions):
        """Get the region centroids as a list of feature dictionaries
        Returns
        -------
        list
            A list of GeoJSON-style dicts, with Point features corresponding to
            region centroids
        """
        return [
            {
                'type': 'Feature',
                'geometry': mapping(shape(region['feature']['geometry']).centroid),
                'properties': {
                    'name': region['name']
                }
            }
            for region in regions
        ]

    @staticmethod
    def _get_coordinates(regions):
        centroids = EDWrapper.centroids_as_features(regions.elements)
        coordinates = basic_functions.get_long_lat_decimal_degrees(centroids)
        return coordinates

    def _calculate_pop_density(self, pop_array_by, region_set_name):
        pop_density = {}
        for region_nr, region in enumerate(pop_array_by.spec.dim_coords(region_set_name).elements):
            area_region = shape(region['feature']['geometry']).area
            population = pop_array_by.as_ndarray()[region_nr]
            pop_density[region['name']] = population / area_region

        return pop_density

    def _get_temperatures(self, data_handle, sim_yrs, regions, constant_weather=False):
        """Load minimum and maximum temperatures
        """
        logging.debug("... load temperature")
        temp_data = defaultdict(dict)

        for simulation_yr in sim_yrs:

            if constant_weather:
                simulation_yr = sim_yrs[0]
            else:
                pass

            t_min = data_handle.get_data('t_min', 2015).as_ndarray()
            t_max = data_handle.get_data('t_max', 2015).as_ndarray()

            for region_nr, region_name in enumerate(regions):
                temp_data[simulation_yr][region_name] = {
                    't_min': t_min[region_nr],
                    't_max': t_max[region_nr]}

        return dict(temp_data)

    def _load_gva_sector_data(self, data_handle, regions):
        """Load sector specific gva data
        """
        out_dict = {}

        gva_sector_data = data_handle.get_base_timestep_data('gva_per_sector')
        sectors_to_load = gva_sector_data.spec.dim_coords('sectors').ids
        sectors_to_load_str = gva_sector_data.spec.dim_coords('sectors').ids
        sectors_to_load = []
        for i in sectors_to_load_str:
            sectors_to_load.append(int(i))

        for gva_sector_nr, sector_id in enumerate(sectors_to_load):
            out_dict[sector_id] = self._assign_array_to_dict(gva_sector_data.as_ndarray()[:, gva_sector_nr], regions)

        return out_dict

    def _load_narrative_parameters(
            self,
            data_handle,
            simulation_base_yr,
            simulation_end_yr,
            default_streategy_vars
        ):
        """
        """
        narrative_params = {}

        # All narrative parameters
        variable_names = [
            'air_leakage',
            'assump_diff_floorarea_pp',
            'cooled_floorarea',
            'dm_improvement',
            'f_eff_achieved',
            'generic_enduse_change',
            'heat_recovered',
            'p_cold_rolling_steel',
            'rs_t_base_heating',
            'ss_t_base_heating',
            'is_t_base_heating',
            'smart_meter_p',
            'generic_fuel_switch']

        for var_name in variable_names:
            logging.debug("... reading in scenaric values for parameter: '{}'".format(var_name))
            param_raw_series = data_handle.get_parameter(var_name).as_df()
            df_raw = self._series_to_df(param_raw_series, var_name)

            narrative_params[var_name] = narrative_related.read_user_defined_param(
                df_raw,
                simulation_base_yr=simulation_base_yr,
                simulation_end_yr=simulation_end_yr,
                default_streategy_var=default_streategy_vars[var_name],
                var_name=var_name)

        return narrative_params

    def before_model_run(self, data_handle):
        """Implement this method to conduct pre-model run tasks
        """
        logging.debug("... Start function before_model_run")
        data = {}

        if self._get_base_yr(data_handle) != 2015:
            msg = "The first defined year in model config does not correspond to \
                   the hardcoded base year"
            raise ValueError(msg)

        path_main = self._get_working_dir()
        config_file_path = os.path.join(path_main, 'wrapperconfig.ini')
        config = data_loader.read_config_file(config_file_path)

        # Replace constrained | unconstrained mode from narrative
        mode = self._get_mode(data_handle)
        config['CRITERIA']['mode_constrained'] = mode

        virtual_building_stock_criteria = self._get_virtual_dw_stock(data_handle)
        config['CRITERIA']['virtual_building_stock_criteria'] = virtual_building_stock_criteria

        logging.debug("MODE {} VIRTUAL_STOCK {}".format(mode, virtual_building_stock_criteria))

        region_set_name = self._get_region_set_name()
        curr_yr = self._get_base_yr(data_handle)
        sim_yrs = self._get_simulation_yrs(data_handle)

        temp_path = config['PATHS']['path_result_data']
        self.create_folders_rename_folders(config)

        # Load hard-coded standard default assumptions
        default_streategy_vars = strategy_vars_def.load_param_assump(
            hard_coded_default_val=True)

        # -----------------------------
        # Reading in narrative variables
        # -----------------------------
        strategy_vars = strategy_vars_def.generate_default_parameter_narratives(
            default_streategy_vars=default_streategy_vars,
            end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            base_yr=config['CONFIG']['base_yr'])

        user_defined_vars = self._load_narrative_parameters(
            data_handle,
            simulation_base_yr=config['CONFIG']['base_yr'],
            simulation_end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            default_streategy_vars=default_streategy_vars)

        strategy_vars = data_loader.replace_variable(user_defined_vars, strategy_vars)

        strategy_vars = strategy_vars_def.autocomplete_strategy_vars(
            strategy_vars,
            narrative_crit=True)

        # ------------------------------------------------
        # Load base year scenario data
        # ------------------------------------------------
        data['scenario_data'] = defaultdict(dict)
        data['scenario_data']['gva_industry'] = defaultdict(dict)
        data['scenario_data']['floor_area'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head')
        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        # Floor area and service building count inputs (not from virtual dwelling stock)
        floor_area_curr = data_handle.get_base_timestep_data('floor_area').as_ndarray()
        data['scenario_data']['rs_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 0], data['regions'])
        data['scenario_data']['ss_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 1], data['regions'])
        data['service_building_count'] = {}
        data['service_building_count'][curr_yr] = []

        data['scenario_data']['population'][curr_yr] = self._assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = self._assign_array_to_dict(gva_array_by.as_ndarray(), data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))
        pop_density = self._calculate_pop_density(pop_array_by, region_set_name)

        data['scenario_data']['gva_industry'][curr_yr] = self._load_gva_sector_data(data_handle, data['regions'])

        # -----------------------------
        # Load temperatures and weather stations
        # -----------------------------
        data['temp_data'] = self._get_temperatures(data_handle, sim_yrs, data['regions'], constant_weather=False)

        # -----------------------------------------
        # Load data
        # ------------------------------------------
        data = wrapper_model.load_data_before_simulation(
            data, sim_yrs, config, curr_yr)

        # Update variables
        data['assumptions'].update('strategy_vars', strategy_vars)
        data['assumptions'].update("rs_regions_without_floorarea", {}) #TODO
        data['assumptions'].update("ss_regions_without_floorarea", {})  #TODO

        technologies = general_assumptions.update_technology_assumption(
            data['assumptions'].technologies,
            data['assumptions'].strategy_vars['f_eff_achieved'],
            data['assumptions'].strategy_vars['gshp_fraction'])
        data['assumptions'].technologies.update(technologies)

        # -----------------------------------------
        # Load switches
        # -----------------------------------------
        switches_service_raw = data_handle.get_parameter('switches_service').as_df()
        switches_service_raw = self._series_to_df(switches_service_raw, 'switches_service')
        service_switches = read_data.service_switch(switches_service_raw)

        fuel_switches = read_data.read_fuel_switches(os.path.join(data['local_paths']['path_strategy_vars'], "switches_fuel.csv"), data['enduses'], data['assumptions'].fueltypes, data['assumptions'].technologies)

        capacity_switches = read_data.read_capacity_switch(os.path.join(data['local_paths']['path_strategy_vars'], "switches_capacity.csv"))

        # -----------------------------------------
        # Perform pre-step calculations
        # ------------------------------------------
        regional_vars, non_regional_vars, fuel_disagg, crit_switch_happening = wrapper_model.before_simulation(
            data,
            config,
            sim_yrs,
            pop_density,
            service_switches,
            fuel_switches,
            capacity_switches)

        # -----------------------------------------
        # Write pre_simulate to disc
        # ------------------------------------------
        write_data.write_yaml(regional_vars, os.path.join(temp_path, "regional_vars.yml"))
        write_data.write_yaml(non_regional_vars, os.path.join(temp_path, "non_regional_vars.yml"))
        write_data.write_yaml(fuel_disagg, os.path.join(temp_path, "fuel_disagg.yml"))
        write_data.write_yaml(crit_switch_happening, os.path.join(temp_path, "crit_switch_happening.yml"))

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Returns
        =======
        supply_results : dict
            key: name defined in sector models
                value: np.zeros((len(reg), len(intervals)) )
        """
        data = {}

        region_set_name = self._get_region_set_name()
        path_main = self._get_working_dir()
        config_file_path = os.path.join(path_main, 'wrapperconfig.ini')
        config = data_loader.read_config_file(config_file_path)

        # Replace constrained | unconstrained mode from narrative
        mode = self._get_mode(data_handle)
        config['CRITERIA']['mode_constrained'] = mode

        virtual_building_stock_criteria = self._get_virtual_dw_stock(data_handle)
        config['CRITERIA']['virtual_building_stock_criteria'] = virtual_building_stock_criteria

        logging.info("MODE {} VIRTUAL_STOCK {}".format(mode, virtual_building_stock_criteria))

        curr_yr = self._get_simulation_yr(data_handle)
        base_yr = config['CONFIG']['base_yr']
        weather_yr = curr_yr

        sim_yrs = self._get_simulation_yrs(data_handle)

        temp_and_result_path = config['PATHS']['path_result_data']

        data['result_paths'] = basic_functions.get_result_paths(temp_and_result_path)
        for path_folder in data['result_paths'].values():
            basic_functions.create_folder(path_folder)

        # --------------------------------------------------
        # Read all other data
        # --------------------------------------------------
        data['scenario_data'] = defaultdict(dict)
        data['scenario_data']['gva_industry'] = defaultdict(dict)
        data['scenario_data']['rs_floorarea'] = defaultdict(dict)
        data['scenario_data']['ss_floorarea'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head').as_ndarray()

        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids
        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        data['scenario_data']['population'][base_yr] = self._assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        data['scenario_data']['gva_per_head'][base_yr] = self._assign_array_to_dict(gva_array_by, data['regions'])
        data['scenario_data']['gva_industry'][base_yr] = self._load_gva_sector_data(data_handle, data['regions'])

        floor_area_base = data_handle.get_base_timestep_data('floor_area').as_ndarray()
        data['scenario_data']['rs_floorarea'][base_yr] = self._assign_array_to_dict(floor_area_base[:, 0], data['regions'])
        data['scenario_data']['ss_floorarea'][base_yr] = self._assign_array_to_dict(floor_area_base[:, 1], data['regions'])

        floor_area_curr = data_handle.get_data('floor_area').as_ndarray()

        data['scenario_data']['rs_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 0], data['regions'])
        data['scenario_data']['ss_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 1], data['regions'])

        # --------------------------------------------
        # Load scenario data for current year
        # --------------------------------------------
        pop_array_cy = data_handle.get_data('population').as_ndarray()
        gva_array_cy = data_handle.get_data('gva_per_head').as_ndarray()

        data['scenario_data']['population'][curr_yr] = self._assign_array_to_dict(pop_array_cy, data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = self._assign_array_to_dict(gva_array_cy, data['regions'])
        data['scenario_data']['gva_industry'][curr_yr] = self._load_gva_sector_data(data_handle, data['regions'])

        floor_area_curr = data_handle.get_data('floor_area').as_ndarray()
        data['scenario_data']['rs_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 0], data['regions'])
        data['scenario_data']['ss_floorarea'][curr_yr] = self._assign_array_to_dict(floor_area_curr[:, 1], data['regions'])

        default_streategy_vars = strategy_vars_def.load_param_assump(
            hard_coded_default_val=True)

        strategy_vars = strategy_vars_def.generate_default_parameter_narratives(
            default_streategy_vars=default_streategy_vars,
            end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            base_yr=config['CONFIG']['base_yr'])

        user_defined_vars = self._load_narrative_parameters(
            data_handle,
            simulation_base_yr=config['CONFIG']['base_yr'],
            simulation_end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            default_streategy_vars=default_streategy_vars)

        strategy_vars = data_loader.replace_variable(user_defined_vars, strategy_vars)

        # Replace strategy variables not defined in csv files)
        strategy_vars = strategy_vars_def.autocomplete_strategy_vars(
            strategy_vars,
            narrative_crit=True)

        # -----------------------------
        # Load temperatures
        # -----------------------------
        data['temp_data'] = self._get_temperatures(
            data_handle, sim_yrs, data['regions'], constant_weather=False)

        # -----------------------------------------
        # Load data
        # -----------------------------------------
        data = wrapper_model.load_data_before_simulation(
            data,
            sim_yrs,
            config,
            curr_yr)
        data['assumptions'].update('strategy_vars', strategy_vars)

        # -----------------------------------------
        # Specific region selection
        # -----------------------------------------
        region_selection = data['regions']

        # Update regions
        setattr(data['assumptions'], 'reg_nrs', len(region_selection))

        # --------------------------------------------------
        # Read results from pre_simulate from disc
        # --------------------------------------------------
        logging.debug("... reading in results from before_model_run(): " + str(temp_and_result_path))
        regional_vars = read_data.read_yaml(os.path.join(temp_and_result_path, "regional_vars.yml"))
        non_regional_vars = read_data.read_yaml(os.path.join(temp_and_result_path, "non_regional_vars.yml"))
        data['fuel_disagg'] = read_data.read_yaml(os.path.join(temp_and_result_path, "fuel_disagg.yml"))
        crit_switch_happening = read_data.read_yaml(os.path.join(temp_and_result_path, "crit_switch_happening.yml"))
        setattr(data['assumptions'], 'crit_switch_happening', crit_switch_happening)
        setattr(data['assumptions'], 'regional_vars', regional_vars)
        setattr(data['assumptions'], 'non_regional_vars', non_regional_vars)

        # --------------------------------------------------
        # Update depending on narratives
        # --------------------------------------------------
        # Update technological efficiencies for specific year according to narrative
        updated_techs = general_assumptions.update_technology_assumption(
            technologies=data['assumptions'].technologies,
            narrative_f_eff_achieved=data['assumptions'].non_regional_vars['f_eff_achieved'][curr_yr],
            narrative_gshp_fraction=data['assumptions'].non_regional_vars['gshp_fraction'][curr_yr],
            crit_narrative_input=False)
        data['assumptions'].technologies.update(updated_techs)

        # --------------------------------------------------
        # Run main model function
        # --------------------------------------------------
        sim_obj = energy_demand_model(
            region_selection,
            data,
            config['CRITERIA'],
            data['assumptions'],
            weather_yr=weather_yr,
            weather_by=data['assumptions'].weather_by)

        # --------------------------------------------------
        # Write other results to txt files
        # --------------------------------------------------
        wrapper_model.write_user_defined_results(
            config['CRITERIA'],
            data['result_paths'],
            sim_obj,
            data,
            curr_yr,
            region_selection,
            pop_array_cy)

        # --------------------------------------------------
        # Pass results to supply model and smif
        # --------------------------------------------------
        for key_name in self.outputs:
            if key_name in sim_obj.supply_results.keys():
                logging.debug("...writing `{}` to smif".format(key_name))
                single_result = sim_obj.supply_results[key_name]
                data_handle.set_results(key_name, single_result)
            else:
                logging.info(" '{}' is not provided and thus replaced with empty values".format(key_name))
                #data_handle.set_results(key_name, np.zeros((391, 8760)))
                logging.info(" '{}' is not in outputs".format(key_name))
                raise Exception("Output '{}' is not defined".format(key_name))
