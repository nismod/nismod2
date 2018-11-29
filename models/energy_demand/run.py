"""The sector model wrapper for smif to run the energy demand model test
as_df())
"""
import os
import configparser
import logging
from collections import defaultdict
from shapely.geometry import shape, mapping

from smif.model.sector_model import SectorModel

from energy_demand import wrapper_model
from energy_demand.assumptions import strategy_vars_def, general_assumptions
from energy_demand.main import energy_demand_model
from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data, read_data, data_loader, narrative_related

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
        """Load all standard variables of parameters
        """
        params = {}

        # Load all scenario parameters
        all_parameter_names = list(data_handle.get_parameters().keys())

        for parameter in all_parameter_names:
            logging.info("... loading standard parameter '{}'".format(parameter))
            loaded_array = data_handle.get_parameter(parameter).as_ndarray()

            try: # Single dim param
                params[parameter] = float(loaded_array)
            except: # Multi dim param
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

    def _series_to_df(self, series, name):
            return series.reset_index().rename(columns={
                0: name
    })

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

    def _calculate_pop_density(self, pop_array_by, region_set_name):
        pop_density = {}
        for region_nr, region in enumerate(pop_array_by.spec.dim_coords(region_set_name).elements):
            area_region = shape(region['feature']['geometry']).area
            population = pop_array_by.as_ndarray()[region_nr]
            pop_density[region['name']] = population / area_region

        return pop_density

    def _get_weather_station_coordinates(self, data_handle):
        """Load coordinates of weather stations
        """
        out_stations = {}

        stations_latitude = data_handle.get_data('latitude', 2015).as_ndarray()
        stations_longitude = data_handle.get_data('longitude', 2015).as_ndarray()

        temperature_input_spec = self.inputs['latitude']
        station_ids = temperature_input_spec.dim_coords('station_id').elements

        for station_array_nr, station_dict in enumerate(station_ids):
            station_id = station_dict['name']
            out_stations[station_id] = {
                'latitude' : stations_latitude[station_array_nr],
                'longitude': stations_longitude[station_array_nr]}

        return out_stations

    def _get_temperatures(self, data_handle, sim_yrs, weather_station_ids):
        """Load minimum and maximum temperatures
        """
        temp_data = defaultdict(dict)

        for simulation_yr in sim_yrs:
            print("... load temperatuer of year {}".format(simulation_yr))
            t_min = data_handle.get_data('t_min', 2015).as_ndarray()
            t_max = data_handle.get_data('t_max', 2015).as_ndarray()

            for array_nr, station_id in enumerate(weather_station_ids):
                temp_data[simulation_yr][station_id] = {
                    't_min': t_min[array_nr],
                    't_max': t_max[array_nr]}

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
            out_dict[sector_id] = assign_array_to_dict(gva_sector_data.as_ndarray()[:, gva_sector_nr], regions)

        return out_dict

    '''def _replace_key_and_restructure(self, df_input):
        """Load parameters and bring in needed format
        """
        df_input = df_input.set_index('enduses')

        dict_input = df_input.to_dict('index')

        dict_output = {}
        for key, values in dict_input.items():
            values_replaced = values
            name_param = values_replaced['interpolation_params']
            values_replaced[name_param] = float(values_replaced['value'])
            del values_replaced['interpolation_params']
            del values_replaced['value']
            dict_output[key] = values_replaced

        return dict_output'''

    def _load_narrative_parameters(
            self,
            data_handle,
            simulation_end_yr,
            simulation_base_yr,
            default_streategy_vars
        ):

        narrative_params = {}

        variable_names = list(data_handle.get_parameters().keys())

        #print("variable_names: " + str(variable_names))
        variable_names = [
            'dm_improvement',
            'is_t_base_heating']

        #var_name = 'is_t_base_heating'
        ##print(data_handle.get_parameter(var_name).shape)
        ##print(data_handle.get_parameter(var_name).dims)
        #raise Exception("WHAT IS THIS??")
        for var_name in variable_names:
            print("... transposing {}".format(var_name))
            param_raw_series = data_handle.get_parameter(var_name).as_df()

            df_raw = self._series_to_df(param_raw_series, var_name)

            var_name_transpsed = narrative_related.transpose_input(
                df_raw,
                simulation_end_yr=simulation_end_yr,
                simulation_base_yr=simulation_base_yr,
                default_streategy_var=default_streategy_vars[var_name],
                var_name=var_name)

            narrative_params[var_name] = var_name_transpsed

        return narrative_params

    def before_model_run(self, data_handle):
        """Implement this method to conduct pre-model run tasks
        """
        logging.info("... Start function before_model_run")
        if self._get_base_yr(data_handle) != 2015:
            raise Exception("The first defined year in model config does not correspond to the hardcoded base year")

        config = self._get_configs()
        region_set_name = self._get_region_set_name()
        
        data = {}
        curr_yr = self._get_base_yr(data_handle)
        sim_yrs = self._get_simulation_yrs(data_handle)
        data['name_scenario_run'], data['result_paths'], temp_path, data['path_new_scenario'] = self._get_config_paths(
            config)

        # TODO SCENARIO PATH
        '''user_defined_config_path = os.path.join(
            config['PATHS']['path_local_data'],
            '00_user_defined_variables_SCENARIO',
            '03_paperI_scenarios',
            name_scenario)'''

        # Load all standard parameters defined in 'data/parameters'
        #TODO These are the standard parameters and not the narratives'
        default_values = self._get_standard_parameters(data_handle)

        #print(default_values['rs_t_heating_by'])
        #raise Exception

        # Load hard-coded standard default assumptions
        default_streategy_vars = strategy_vars_def.load_param_assump(
            #default_values=default_values,
            hard_coded_default_val=True) #FALSE

        # Create marratovs from all default parameters #NEW
        strategy_vars = strategy_vars_def.load_smif_parameters(
            default_streategy_vars=default_streategy_vars,
            end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            base_yr=config['CONFIG']['base_yr'],
            mode='local')
            
        # LODAD DM PARAMETER
        user_defined_vars = self._load_narrative_parameters(
            data_handle,
            simulation_end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            simulation_base_yr=config['CONFIG']['base_yr'],
            default_streategy_vars=default_streategy_vars)

        strategy_vars = data_loader.replace_variable(user_defined_vars, strategy_vars)

        # Replace strategy variables not defined in csv files)
        strategy_vars_out = strategy_vars_def.autocomplete_strategy_vars(
            strategy_vars,
            narrative_crit=True)

        #data['assumptions'].update('strategy_vars', strategy_vars_out)


        '''# LOAD FROM SCENARIOS 
        narrative_variables = narrative_variables,  # All narrative variables
        loaded_narrative_data =                     # All narrative data
        # =================
        # Idential to reading in raw files from folder (multidimensional narratives)
        # =================
        load_user_defined_vars()

        narative_data = data_loader.load_smif_narrative_data(
            default_strategy_var=default_streategy_vars,
            narrative_variables=narrative_variables,
            loaded_narrative_data=loaded_narrative_data,
            simulation_base_yr=data['assumptions'].base_yr,
            simulation_end_yr=data['assumptions'].simulation_end_yr)

        # Replace standard narratives with user defined narratives from .csv files
        strategy_vars = data_loader.replace_variable(
            narative_data, strategy_vars)

        strategy_vars_out = strategy_vars_def.autocomplete_strategy_vars(strategy_vars, narrative_crit=True)
        data['assumptions'].update('strategy_vars', strategy_vars_out)
        '''
        #narrative_values = {}
        #
        ## Create single standard narrative (DEFAULT)
        #strategy_vars = strategy_vars_def.load_smif_parameters(
        #    narrative_values=narrative_values,
        #    default_streategy_vars=default_streategy_vars,
        #    end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
        #    base_yr=config['CONFIG']['base_yr'],
        #    mode='smif')

        # ------------------------------------------------
        # Load base year scenario data
        # ------------------------------------------------
        data['scenario_data'] = defaultdict(dict)
        data['scenario_data']['gva_industry'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head')
        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        data['scenario_data']['population'][curr_yr] = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = assign_array_to_dict(gva_array_by.as_ndarray(), data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))
        pop_density = self._calculate_pop_density(pop_array_by, region_set_name)

        # Load sector specific GVA data, if available
        data['scenario_data']['gva_industry'][curr_yr] = self._load_gva_sector_data(data_handle, data['regions'])

        # -----------------------------
        # Load temperatures and weather stations
        # -----------------------------
        data['weather_stations'] = self._get_weather_station_coordinates(data_handle)
        data['temp_data'] = self._get_temperatures(data_handle, sim_yrs, data['weather_stations'])

        # -----------------------------------------
        # Load data
        # ------------------------------------------
        data = wrapper_model.load_data_before_simulation(
            data,
            sim_yrs,
            config,
            curr_yr)
        data['assumptions'].update('strategy_vars', strategy_vars)

        technologies = general_assumptions.update_technology_assumption(
            data['assumptions'].technologies,
            data['assumptions'].strategy_vars['f_eff_achieved'],
            data['assumptions'].strategy_vars['gshp_fraction_ey'])
        data['assumptions'].technologies.update(technologies)

        # -----------------------------------------
        # Load switches from intervention
        # TODO REPLACE WITH INTERVENTION??
        # -----------------------------------------
        service_switches = read_data.service_switch(os.path.join(data['local_paths']['path_strategy_vars'], "switches_service.csv"), data['assumptions'].technologies)
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
        base_yr = config['CONFIG']['base_yr']
        weather_yr = config['CONFIG']['weather_yr_scenario']
        sim_yrs = self._get_simulation_yrs(data_handle)

        data['name_scenario_run'], data['result_paths'], temp_path, data['path_new_scenario'] = self._get_config_paths(config)

        # --------------------------------------------------
        # Read all other data
        # --------------------------------------------------
        data['scenario_data'] = defaultdict(dict)
        data['scenario_data']['gva_industry'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head').as_ndarray()

        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids
        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        data['scenario_data']['population'][base_yr] = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        data['scenario_data']['gva_per_head'][base_yr] = assign_array_to_dict(gva_array_by, data['regions'])
        data['scenario_data']['gva_industry'][base_yr] = self._load_gva_sector_data(data_handle, data['regions'])

        # --------------------------------------------
        # Load scenario data for current year
        # --------------------------------------------
        pop_array_cy = data_handle.get_data('population').as_ndarray()
        gva_array_cy = data_handle.get_data('gva_per_head').as_ndarray()

        data['scenario_data']['population'][curr_yr] = assign_array_to_dict(pop_array_cy, data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = assign_array_to_dict(gva_array_cy, data['regions'])
        data['scenario_data']['gva_industry'][curr_yr] = self._load_gva_sector_data(data_handle, data['regions'])


        #default_values = self._get_standard_parameters(data_handle)
        default_streategy_vars = strategy_vars_def.load_param_assump(
            #default_values=default_values,
            hard_coded_default_val=True)

        narrative_values = {}
        strategy_vars = strategy_vars_def.load_smif_parameters(
            narrative_values=narrative_values,
            default_streategy_vars=default_streategy_vars,
            end_yr=config['CONFIG']['user_defined_simulation_end_yr'],
            base_yr=config['CONFIG']['base_yr'])

        raw_file_content_service_switches = [] # data_handle.get_parameter('switches_service')
        
        # -----------------------------
        # Load temperatures
        # -----------------------------
        data['weather_stations'] = self._get_weather_station_coordinates(data_handle)
        data['temp_data'] = self._get_temperatures(data_handle, sim_yrs, data['weather_stations'])

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
        crit_switch_happening = read_data.read_yaml(os.path.join(temp_path, "crit_switch_happening.yml"))
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
            region_selection)

        # --------------------------------------------------
        # Pass results to supply model and smif
        # --------------------------------------------------
        for key_name, result_to_txt in sim_obj.supply_results.items():
            if key_name in self.outputs:
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
