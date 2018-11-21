"""The sector model wrapper for smif to run the energy demand model test

TODO: CHANGE 'latitude' : float(row['Latitude']),
"""
import os
import configparser
import logging
from collections import defaultdict
from shapely.geometry import shape, mapping

from smif.model.sector_model import SectorModel

from energy_demand.assumptions import strategy_vars_def
from energy_demand.read_write import narrative_related

from energy_demand.assumptions import general_assumptions
from energy_demand import wrapper_model
from energy_demand.main import energy_demand_model
from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.read_write import data_loader

def load_smif_parameters_NEW(
        scenario_values,
        default_streategy_vars=False,
        end_yr=2050,
        base_yr=2015):
    strategy_vars = defaultdict(dict)

    # ------------------------------------------------------------
    # Create default narrative for every simulation parameter
    # ------------------------------------------------------------
    for var_name, var_entries in default_streategy_vars.items():
        crit_single_dim = narrative_related.crit_dim_var(var_entries)

        if crit_single_dim:
            try:
                scenario_value = scenario_values[var_name]
            except:
                logging.info("IMPORTANT WARNING: Pparamter could not be loaded from smif: `%s`", var_name)
                scenario_value = var_entries['default_value']

            # Create default narrative with only one timestep from simulation base year to simulation end year
            strategy_vars[var_name] = narrative_related.default_narrative(
                end_yr=end_yr,
                value_by=var_entries['default_value'],                # Base year value,
                value_ey=scenario_value,
                diffusion_choice=var_entries['diffusion_type'],       # Sigmoid or linear,
                base_yr=base_yr,
                regional_specific=var_entries['regional_specific'])   # Criteria whether the same for all regions or not

        else:
            # Standard narrative for multidimensional narrative
            for sub_var_name, sub_var_entries in var_entries.items():
                try:
                    scenario_value = scenario_values[var_name]
                except:
                    logging.warning("IMPORTANT WARNING: The paramter `%s` could not be loaded from smif ", var_name)
                    scenario_value = sub_var_entries['scenario_value']

                strategy_vars[var_name][sub_var_name] = narrative_related.default_narrative(
                    end_yr=end_yr,
                    value_by=sub_var_entries['default_value'],
                    value_ey=scenario_value,
                    diffusion_choice=sub_var_entries['diffusion_type'],
                    base_yr=base_yr,
                    regional_specific=sub_var_entries['regional_specific'])

    return strategy_vars

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)
        self.user_data = {}

    def _assign_array_to_dict(array_in, regions):
        """Convert array to dict with same order as region list

        Input
        -----
        regions : list
            List with specific order of regions
        array_in : array
            Data array with data like the order of the region list

        Returns
        -------
        dict_out : dict
            Dictionary of array_in
        """
        dict_out = {}
        for r_idx, region in enumerate(regions):
            dict_out[region] = array_in[r_idx]
        return dict_out

    def _get_working_dir(self):
        """Get path
        """
        return os.path.dirname(os.path.abspath(__file__))

    def _get_configs(self):
        """Get all configurations from .ini file

        If 0: False, if 1: True
        """
        path_main = self._get_working_dir()
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        # Save config in dict and get correct type
        config = basic_functions.convert_config_to_correct_type(config)

        return config

    def _get_config_paths(self, config):
        """Create scenario name and get paths
        """
        name_scenario = "scenario_A" #str(data_handle['config_folder_path']) #TODO
        temp_path = os.path.normpath(config['PATHS']['path_result_data'])

        path_new_scenario = os.path.join(temp_path, name_scenario)
        result_paths = data_loader.get_result_paths(path_new_scenario)

        # ------------------------------
        # Delete previous model results and create result folders
        # ------------------------------
        basic_functions.del_previous_setup(result_paths['data_results'])
        basic_functions.create_folder(path_new_scenario)

        folders_to_create = [
            result_paths['data_results_model_run_pop'],
            result_paths['data_results_validation']]

        for folder in folders_to_create:
            basic_functions.create_folder(folder)

        return name_scenario, result_paths, temp_path, path_new_scenario

    def _get_standard_parameters(self, data_handle):
        """Read float values
        """
        # Load all standard variables of parameters
        all_parameter_names = list(data_handle.get_parameters().keys())
        print("AL PARAMS " + str(all_parameter_names))
        params = {}
        for parameter in all_parameter_names:
            logging.info("... loading standard parameter '{}'".format(parameter))
            loaded_array = data_handle.get_parameter(parameter).as_ndarray()
            try:
                # Single dim param
                params[parameter] = float(loaded_array)
            except:
                # Multi dim param
                params[parameter] = loaded_array
  
        return params

    def _get_region_set_name(self):
        return 'lad_uk_2016'

    def _get_base_yr(self, data_handle):
        return data_handle.timesteps[0]

    def _get_simulation_yr(self, data_handle):
        return data_handle.current_timestep

    def _get_simulation_yrs(self, data_handle):
        return data_handle.timesteps

    def centroids_as_features(self, regions):
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

    def _get_coordinates(self, regions):
        centroids = self.centroids_as_features(regions.elements)
        coordinates = basic_functions.get_long_lat_decimal_degrees(centroids)
        return coordinates

    def before_model_run(self, data_handle):
        """Implement this method to conduct pre-model run tasks
        """
        if self._get_base_yr(data_handle) != 2015:
            raise Exception("The first defined year in model config does not correspond to the hardcoded base year")

        config = self._get_configs()
        region_set_name = self._get_region_set_name()
        logging.info("============Start before_model_run===============================================")
        data = {}

        curr_yr = self._get_base_yr(data_handle)
        simulation_yrs = self._get_simulation_yrs(data_handle)
        data['name_scenario_run'], data['result_paths'], temp_path, data['path_new_scenario'] = self._get_config_paths(
            config)

        # ---------
        # LOAD ALL NARRATIVE PARAMS
        # ----------NEW
        #print(data_handle.get_parameter('spatial_explicit_diffusion').as_ndarray())
        #print(data_handle.get_scenario('temperatures').as_ndarray())

        default_values = self._get_standard_parameters(data_handle)

        '''default_values = {
            'spatial_explicit_diffusion': own_data_handler_parameters['spatial_explicit_diffusion'],
            'speed_con_max': own_data_handler_parameters['speed_con_max'],
            'gshp_fraction': own_data_handler_parameters['gshp_fraction'],
            'rs_t_heating_by': own_data_handler_parameters['rs_t_heating_by'],
            'ss_t_heating_by': own_data_handler_parameters['ss_t_heating_by'],
            'ss_t_cooling_by': own_data_handler_parameters['ss_t_cooling_by'],
            'is_t_heating_by': own_data_handler_parameters['is_t_heating_by'],
            'smart_meter_p_by': own_data_handler_parameters['smart_meter_p_by'],
            'cooled_ss_floorarea_by': own_data_handler_parameters['cooled_ss_floorarea_by'],
            'p_cold_rolling_steel_by': own_data_handler_parameters['p_cold_rolling_steel_by']}'''
        default_streategy_vars = strategy_vars_def.load_param_assump(
            default_values=default_values)



        # ----------NEW
        '''# LOAD FROM SCENARIOS
        _user_defined_vars = data_loader.load_user_defined_vars(
                default_strategy_var=default_streategy_vars,
                path_csv=user_defined_config_path,
                simulation_base_yr=data['assumptions'].base_yr,
                simulation_end_yr=data['assumptions'].simulation_end_yr)

        logging.info("All user_defined parameters %s", _user_defined_vars.keys())
        # --------------------------------------------------------
        # Replace standard narratives with user defined narratives from .csv files
        # --------------------------------------------------------
        strategy_vars = data_loader.replace_variable(
            _user_defined_vars, strategy_vars)'''
        scenario_values = {}
        strategy_vars = load_smif_parameters_NEW(
            scenario_values=scenario_values,
            default_streategy_vars=default_streategy_vars,
            end_yr=2050,
            base_yr=2015) #TODO REPLACE

        # ------------------------------------------------
        # Load base year scenario data
        # ------------------------------------------------
        data['scenario_data'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')     # Population
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head')   # Overall GVA per head
        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        #TODO GET TEMPERATURES
        #data['temp_data']  = data_handle.get_base_timestep_data('temperatures')
        #data['weather_stations'] = data_handle.get_base_timestep_data('weather_stations')
        pop_array_by_new = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        gva_array_by_new = assign_array_to_dict(gva_array_by.as_ndarray(), data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        pop_density = {}
        for region_nr, region in enumerate(pop_array_by.spec.dim_coords(region_set_name).elements):
            area_region = shape(region['feature']['geometry']).area
            population = pop_array_by.as_ndarray()[region_nr]
            pop_density[region['name']] = population / area_region

        # Load sector specific GVA data, if available
        sector_gva_data = {}
        gva_sector_data = data_handle.get_base_timestep_data('gva_per_sector')
        
        sectors_to_load = gva_sector_data.spec.dim_coords('sectors').ids #sectors to load from dimension file #TODO STR NOT INT
        '''sectors_to_load_str = gva_sector_data.spec.dim_coords('sectors').ids #sectors to load from dimension file #TODO STR NOT INT
        sectors_to_load = []
        for i in sectors_to_load_str:
            sectors_to_load.append(int(i))'''

        for gva_sector_nr, sector_id in enumerate(sectors_to_load):
            sector_gva_data[sector_id] = assign_array_to_dict(gva_sector_data.as_ndarray()[:, gva_sector_nr], data['regions'])

        # -----------------------------------------
        # Load data
        # ------------------------------------------
        logging.info("============ A ===============================================")
        data = wrapper_model.load_data_before_simulation(
            data,
            simulation_yrs,
            config,
            curr_yr,
            pop_array_by_new,
            gva_array_by_new,
            sector_gva_data,
            strategy_vars)

        # -----------------------------------------
        # Perform pre-step calculations
        # ------------------------------------------
        logging.info("============ B ===============================================")
        regional_vars, non_regional_vars, fuel_disagg = wrapper_model.before_simulation(
            data,
            config,
            simulation_yrs,
            pop_density)

        # -----------------------------------------
        # Write pre_simulate to disc
        # ------------------------------------------
        logging.info("============blablan===============================================")
        logging.info("... writing results to disc from before_model_run() " + str(temp_path))
        write_data.write_yaml(regional_vars, os.path.join(temp_path, "regional_vars.yml"))
        write_data.write_yaml(non_regional_vars, os.path.join(temp_path, "non_regional_vars.yml"))
        write_data.write_yaml(fuel_disagg, os.path.join(temp_path, "fuel_disagg.yml"))

        # ------------------------------------------------
        # Plotting
        # ------------------------------------------------
        ##wrapper_model.plots(data, curr_yr, fuel_disagg, config)

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
        config = self._get_configs()

        curr_yr = self._get_simulation_yr(data_handle)
        simulation_yrs = self._get_simulation_yrs(data_handle)

        data['name_scenario_run'], data['result_paths'], temp_path, data['path_new_scenario'] = self._get_config_paths(
            config)

        # --------------------------------------------------
        # Read all other data
        # --------------------------------------------------
        data['scenario_data'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head').as_ndarray()
        gva_sector_data = data_handle.get_base_timestep_data('gva_per_sector')

        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        pop_array_by_new = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        gva_array_by_new = assign_array_to_dict(gva_array_by, data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        # Load sector specific GVA data, if available
        sectors_to_load = gva_sector_data.spec.dim_coords('sectors').ids #sectors to load from dimension file
        '''sectors_to_load_str = gva_sector_data.spec.dim_coords('sectors').ids #sectors to load from dimension file
        sectors_to_load = []
        for i in sectors_to_load_str:
            sectors_to_load.append(int(i))'''

        sector_gva_data = {}
        for gva_sector_nr, sector_id in enumerate(sectors_to_load):
            single_sector_data = gva_sector_data.as_ndarray()[:, gva_sector_nr]
            sector_gva_data[sector_id] = assign_array_to_dict(single_sector_data, data['regions'])

        # --------------------------------------------
        # Load scenario data for current year
        # --------------------------------------------
        pop_array_cy = data_handle.get_data('population').as_ndarray()
        gva_array_cy = data_handle.get_data('gva_per_head').as_ndarray()

        data['scenario_data']['population'][curr_yr] = assign_array_to_dict(pop_array_cy, data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = assign_array_to_dict(gva_array_cy, data['regions'])

        default_values = self._get_standard_parameters(data_handle)

        '''default_values = {
            'spatial_explicit_diffusion': int(own_data_handler_parameters['spatial_explicit_diffusion']),
            'speed_con_max': 1,
            'gshp_fraction': 0.1,
            'rs_t_heating_by': 15.5,
            'ss_t_heating_by': 15.5,
            'ss_t_cooling_by': 5,
            'is_t_heating_by': 15.5,
            'smart_meter_p_by': 0.05,
            'cooled_ss_floorarea_by': 0.35,
            'p_cold_rolling_steel_by': 0.2}'''

        default_streategy_vars = strategy_vars_def.load_param_assump(
            default_values=default_values)

        scenario_values = {}
        strategy_vars = load_smif_parameters_NEW(
            scenario_values=scenario_values,
            default_streategy_vars=default_streategy_vars,
            end_yr=2050,
            base_yr=2015) #TODO REPLACE

        # -----------------------------------------
        # Load data
        # -----------------------------------------
        data = wrapper_model.load_data_before_simulation(
            data,
            simulation_yrs,
            config,
            curr_yr,
            pop_array_by_new,
            gva_array_by_new,
            sector_gva_data,
            strategy_vars)

        # -----------------------------------------
        # Specific region selection
        # -----------------------------------------
        if config['CRITERIA']['reg_selection']:
            region_selection = read_data.get_region_selection(
                os.path.join(data['local_paths']['local_path_datafolder'],
                "region_definitions",
                config['CRITERIA']['reg_selection_csv_name']))
            #region_selection = ['E02003237', 'E02003238']
        else:
            region_selection = data['regions']

        # Update regions
        setattr(data['assumptions'], 'reg_nrs', len(region_selection))

        # --------------------------------------------------
        # Read results from pre_simulate from disc
        # --------------------------------------------------
        logging.info("... reading in results from before_model_run()" + str(temp_path))
        regional_vars = read_data.read_yaml(os.path.join(temp_path, "regional_vars.yml"))
        non_regional_vars = read_data.read_yaml(os.path.join(temp_path, "non_regional_vars.yml"))
        data['fuel_disagg'] = read_data.read_yaml(os.path.join(temp_path, "fuel_disagg.yml"))
        setattr(data['assumptions'], 'regional_vars', regional_vars)
        setattr(data['assumptions'], 'non_regional_vars', non_regional_vars)

        # --------------------------------------------------
        # Update depending on narratives
        # --------------------------------------------------
        # Update technological efficiencies for specific year according to narrative
        updated_techs = general_assumptions.update_technology_assumption(
            technologies=data['assumptions'].technologies,
            narrative_f_eff_achieved=data['assumptions'].non_regional_vars['f_eff_achieved'][curr_yr],
            narrative_gshp_fraction_ey=data['assumptions'].non_regional_vars['gshp_fraction_ey'][curr_yr],
            crit_narrative_input=False)
        data['assumptions'].technologies.update(updated_techs)

        # Write population data to file

        write_data.write_scenaric_population_data(
            curr_yr,
            os.path.join(data['path_new_scenario'], 'model_run_pop'),
            pop_array_cy)

        # --------------------------------------------------
        # Run main model function
        # --------------------------------------------------
        sim_obj = energy_demand_model(
            region_selection,
            data,
            config['CRITERIA'],
            data['assumptions'],
            data['weather_stations'],
            config['CONFIG']['weather_yr_scenario'],
            data['assumptions'].weather_by)

        # --------------------------------------------------
        # Write other results to txt files
        # --------------------------------------------------
        wrapper_model.write_user_defined_results(
            config['CRITERIA'],
            data['result_paths'],
            sim_obj,
            data,
            curr_yr,
            region_selection)

        # --------------------------------------------------
        # Pass results to smif
        # --------------------------------------------------
        for key_name, result_to_txt in sim_obj.supply_results.items():
            if key_name in self.outputs.names:
                data_handle.set_results(key_name, result_to_txt)

        print("---- FIHISHED WRAPPER -----")
        return sim_obj.supply_results

def assign_array_to_dict(array_in, regions):
    """Convert array to dict with same order as region list

    Input
    -----
    regions : list
        List with specific order of regions
    array_in : array
        Data array with data like the order of the region list

    Returns
    -------
    dict_out : dict
        Dictionary of array_in
    """
    dict_out = {}
    for r_idx, region in enumerate(regions):
        dict_out[region] = array_in[r_idx]

    return dict_out
