"""The sector model wrapper for smif to run the energy demand model test
"""
import os
import configparser
import logging
from collections import defaultdict
from shapely.geometry import shape, mapping

from smif.model.sector_model import SectorModel

from energy_demand.assumptions import general_assumptions
from energy_demand import wrapper_model
from energy_demand.main import energy_demand_model
from energy_demand.basic import basic_functions
from energy_demand.read_write import write_data
from energy_demand.read_write import read_data
from energy_demand.read_write import data_loader

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
        name_scenario = "TEST_NAME" #str(data_handle['config_folder_path'])
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

        data = {}

        curr_yr = self._get_base_yr(data_handle)
        simulation_yrs = self._get_simulation_yrs(data_handle)

        data['name_scenario_run'], data['result_paths'], temp_path, data['path_new_scenario'] = self._get_config_paths(
            config)

        # ------------------------------------------------
        # Load base year scenario data
        # ------------------------------------------------
        data['scenario_data'] = defaultdict(dict)

        pop_array_by = data_handle.get_base_timestep_data('population')     # Population
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head')   # Overall GVA per head
        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        pop_array_by_new = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        gva_array_by_new = assign_array_to_dict(gva_array_by.as_ndarray(), data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        pop_density = {}
        for region_nr, region in enumerate(pop_array_by.spec.dim_coords(region_set_name).elements):
            pop_density[region.name] = pop_array_by.as_ndarray()[region_nr] / region.shape.area

        # Load sector specific GVA data, if available
        sectors_to_load = [2, 3, 4, 5, 6, 8, 9, 29, 11, 12, 10, 15, 14, 19, 17, 40, 41, 28, 35, 23, 27]
        sector_data = {}
        for gva_sector_nr in sectors_to_load:
            gva_sector_data = data_handle.get_base_timestep_data('gva_per_head_sector__{}'.format(gva_sector_nr))
            sector_data[gva_sector_nr] = assign_array_to_dict(gva_sector_data.as_ndarray(), regions)

        # -----------------------------------------
        # Load data
        # ------------------------------------------
        data = wrapper_model.load_data_before_simulation(
            data,
            simulation_yrs,
            config,
            curr_yr,
            pop_array_by_new,
            gva_array_by_new,
            gva_data)

        # -----------------------------------------
        # Perform pre-step calculations
        # ------------------------------------------
        regional_vars, non_regional_vars, fuel_disagg = wrapper_model.before_simulation(
            data,
            config,
            simulation_yrs,
            pop_density)

        # -----------------------------------------
        # Write pre_simulate to disc
        # ------------------------------------------
        logging.info("... writing results to disc from before_model_run()")
        wrapper_model.write_yaml(regional_vars, os.path.join(temp_path, "regional_vars.yml"))
        wrapper_model.write_yaml(non_regional_vars, os.path.join(temp_path, "non_regional_vars.yml"))
        wrapper_model.write_yaml(fuel_disagg, os.path.join(temp_path, "fuel_disagg.yml"))

        # ------------------------------------------------
        # Plotting
        # ------------------------------------------------
        wrapper_model.plots(data, curr_yr, fuel_disagg, config)

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

        pop_array_by = data_handle.get_base_timestep_data('population')     # Population
        gva_array_by = data_handle.get_base_timestep_data('gva_per_head')   # Overall GVA per head


        data['regions'] = pop_array_by.spec.dim_coords(region_set_name).ids

        pop_array_by_new = assign_array_to_dict(pop_array_by.as_ndarray(), data['regions'])
        gva_array_by_new = assign_array_to_dict(gva_array_by.as_ndarray(), data['regions'])

        data['reg_coord'] = self._get_coordinates(pop_array_by.spec.dim_coords(region_set_name))

        # Load sector specific GVA data, if available
        sectors_to_load = [2, 3, 4, 5, 6, 8, 9, 29, 11, 12, 10, 15, 14, 19, 17, 40, 41, 28, 35, 23, 27]
        sector_data = {}
        for gva_sector_nr in sectors_to_load:
            gva_sector_data = data_handle.get_base_timestep_data('gva_per_head_sector__{}'.format(gva_sector_nr))
            sector_data[gva_sector_nr] = assign_array_to_dict(gva_sector_data.as_ndarray(), regions)
        # --------------------------------------------
        # Load scenario data for current year
        # --------------------------------------------
        pop_array_cy = data_handle.get_data('population')
        gva_array_cy = data_handle.get_data('gva_per_head')

        data['scenario_data']['population'][curr_yr] = assign_array_to_dict(pop_array_cy.as_ndarray(), data['regions'])
        data['scenario_data']['gva_per_head'][curr_yr] = assign_array_to_dict(gva_array_cy.as_ndarray(), data['regions'])

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
            gva_data)

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
        logging.info("... reading in results from before_model_run()")
        regional_vars = wrapper_model.read_yaml(os.path.join(temp_path, "regional_vars.yml"))
        non_regional_vars = wrapper_model.read_yaml(os.path.join(temp_path, "non_regional_vars.yml"))
        data['fuel_disagg'] = wrapper_model.read_yaml(os.path.join(temp_path, "fuel_disagg.yml"))
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
            pop_array_cy[:, 0])

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