"""The sector model wrapper for smif to run the energy demand model test
"""
import os
import logging
import configparser
import datetime
import time

from collections import defaultdict
import numpy as np
from smif.model.sector_model import SectorModel
from pkg_resources import Requirement, resource_filename
from pyproj import Proj, transform
from energy_demand.plotting import plotting_results
from energy_demand.basic import basic_functions
from energy_demand.scripts.init_scripts import scenario_initalisation
from energy_demand.read_write import write_data
from energy_demand.read_write import data_loader
from energy_demand.main import energy_demand_model
from energy_demand.assumptions import param_assumptions
from energy_demand.assumptions import non_param_assumptions
from energy_demand.basic import date_prop
from energy_demand.validation import lad_validation
from energy_demand.basic import lookup_tables

# -----------
# INFORMATION:
# you only running smif, use the following configuration: FAST_SMIF_RUN == True
# -----------
FAST_SMIF_RUN = True
WRITEOUTSMIFRESULTS = True # Set to True

NR_OF_MODELLEd_REGIONS = 391 # uk: 391 (including ireland), england.: 380

class EDWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)

        self.user_data = {}

    def before_model_run(self, data_handle):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)
        """
        self.user_data['data'] = defaultdict(dict)

        self.user_data['data']['criterias']['mode_constrained'] = True                    # True: Technologies are defined in ED model and fuel is provided, False: Heat is delievered not per technologies
        self.user_data['data']['criterias']['virtual_building_stock_criteria'] = True     # True: Run virtual building stock model
        self.user_data['data']['criterias']['spatial_explicit_diffusion'] = False         # True: Spatial explicit calculations
        self.user_data['data']['criterias']['flat_heat_pump_profile'] = False         # True: Spatial explicit calculations

        if FAST_SMIF_RUN == True:
            self.user_data['data']['criterias']['write_to_txt'] = False
            self.user_data['data']['criterias']['beyond_supply_outputs'] = False
            self.user_data['data']['criterias']['validation_criteria'] = False    # For validation, the mode_constrained must be True
            self.user_data['data']['criterias']['plot_tech_lp'] = False
            self.user_data['data']['criterias']['plot_crit'] = False
            self.user_data['data']['criterias']['crit_plot_enduse_lp'] = False
            self.user_data['data']['criterias']['plot_HDD_chart'] = False
            self.user_data['data']['criterias']['writeYAML'] = False
        else:
            self.user_data['data']['criterias']['write_to_txt'] = True
            self.user_data['data']['criterias']['beyond_supply_outputs'] = True
            self.user_data['data']['criterias']['validation_criteria'] = True
            self.user_data['data']['criterias']['plot_tech_lp'] = False
            self.user_data['data']['criterias']['plot_crit'] = False
            self.user_data['data']['criterias']['crit_plot_enduse_lp'] = True
            self.user_data['data']['criterias']['plot_HDD_chart'] = False
            self.user_data['data']['criterias']['writeYAML'] = True #set to false

        if self.user_data['data']['criterias']['mode_constrained']:
            logging.info("constrained mode where technologies are defined in in HIRE")
        else:
            logging.info("unconstrained mode where technologies are in supply model and heat is provided as output")

        # -----------------------------
        # Paths
        # -----------------------------
        base_yr = 2015 #data_handle.timesteps[0]      # Define base year
        path_main = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))

        self.user_data['data']['data_path'] = config['PATHS']['path_local_data']
        self.user_data['data']['processed_path'] = config['PATHS']['path_processed_data']
        self.user_data['data']['result_path'] = config['PATHS']['path_result_data']

        self.user_data['data']['paths'] = data_loader.load_paths(
            resource_filename(
                Requirement.parse("energy_demand"),
                os.path.join("energy_demand", "config_data")))

        # downloaded (FTP) data
        self.user_data['data']['local_paths'] = data_loader.load_local_paths(
            self.user_data['data']['data_path'])

        # -------------
        # result path
        # -------------
        time_now = str(time.ctime()).replace(":", "_").replace(" ", "_")
        name_scenario_run = "_result_data_{}".format(time_now)

        self.user_data['data']['result_paths'] = data_loader.load_result_paths(
            os.path.join(self.user_data['data']['result_path'], name_scenario_run))

        # -----------------------------
        # Region related info
        # -----------------------------
        region_set_name = 'lad_uk_2016'
        logging.info("Region set name: {}".format(region_set_name))

        self.user_data['data']['regions'] = data_handle.get_region_names(region_set_name)

        reg_centroids = self.get_region_centroids(region_set_name)
        self.user_data['data']['reg_coord'] = self.get_long_lat_decimal_degrees(reg_centroids)

        # SCRAP REMOVE: ONLY SELECT NR OF MODELLED REGIONS
        self.user_data['data']['regions'] = self.user_data['data']['regions'][:NR_OF_MODELLEd_REGIONS]
        self.user_data['data']['reg_nrs'] = len(self.user_data['data']['regions'])

        # ---------------------
        # Energy demand specific input which need to generated or read in
        # ---------------------
        self.user_data['data']['lookups'] = lookup_tables.basic_lookups()
        self.user_data['data']['weather_stations'], self.user_data['data']['temp_data'] = data_loader.load_temp_data(self.user_data['data']['local_paths'] )
        self.user_data['data']['enduses'], self.user_data['data']['sectors'], self.user_data['data']['fuels'] = data_loader.load_fuels(
            self.user_data['data']['paths'], self.user_data['data']['lookups'])

        # ------------
        # Load assumptions
        # ------------
        assumptions = non_param_assumptions.Assumptions(
            base_yr=base_yr,
            curr_yr=data_handle.timesteps[0],
            simulated_yrs=self.timesteps,
            paths=self.user_data['data']['paths'],
            enduses=self.user_data['data']['enduses'],
            sectors=self.user_data['data']['sectors'],
            fueltypes=self.user_data['data']['lookups']['fueltypes'],
            fueltypes_nr=self.user_data['data']['lookups']['fueltypes_nr'])

        strategy_variables = param_assumptions.load_param_assump(
            self.user_data['data']['paths'], self.user_data['data']['local_paths'] , assumptions)
        assumptions.update('strategy_variables', strategy_variables)

        # -----------------------------
        # Obtain external base year scenario data
        # -----------------------------
        pop_array_by = data_handle.get_base_timestep_data('population')
        gva_array_by = data_handle.get_base_timestep_data('gva')
        #industry_gva_by = data_handle.get_base_timestep_data('industry_gva')

        pop_dict = {}
        gva_dict = {}
        gva_industry_dict = {}

        for r_idx, region in enumerate(self.user_data['data']['regions']):
            pop_dict[region] = pop_array_by[r_idx, 0]
            gva_dict[region] = gva_array_by[r_idx, 0]
            #gva_industry_dict[region] = industry_gva_by[r_idx, 0]

        self.user_data['data']['population'][assumptions.base_yr] = pop_dict
        self.user_data['data']['gva'][assumptions.base_yr] = gva_dict
        #self.user_data['data']['industry_gva'][assumptions.base_yr] = gva_industry_dict
        self.user_data['data']['industry_gva'] = "TST"

        # Get building related data
        if self.user_data['data']['criterias']['virtual_building_stock_criteria']:
            self.user_data['data']['rs_floorarea'], self.user_data['data']['ss_floorarea'] = data_loader.floor_area_virtual_dw(
                self.user_data['data']['regions'],
                self.user_data['data']['sectors']['all_sectors'],
                self.user_data['data']['local_paths'],
                base_yr=assumptions.base_yr,
                f_mixed_floorarea=assumptions.f_mixed_floorarea)
        else:
            pass
            # Load floor area from newcastle
            #rs_floorarea = defaultdict(dict)
            #ss_floorarea = defaultdict(dict)

        # -----------------------
        # Calculate population density for base year
        # -----------------------
        #self.user_data['data']['pop_density'] = {}
        for region in self.regions.get_entry(region_set_name):
            try:
                self.user_data['data']['pop_density'][region.name] = self.user_data['data']['population'][assumptions.base_yr][region.name] / region.shape.area
            except:
                self.user_data['data']['pop_density'][region.name] = 1

        # --------------
        # Scenario data
        # --------------
        self.user_data['data']['scenario_data'] = {
            'gva': self.user_data['data']['gva'],
            'population': self.user_data['data']['population'],
            'industry_gva': self.user_data['data']['industry_gva'],
            'floor_area': {
                'rs_floorarea': self.user_data['data']['rs_floorarea'],
                'ss_floorarea': self.user_data['data']['ss_floorarea']
                }
        }

        # ------------
        # Load load profiles of technologies
        # ------------
        self.user_data['data']['tech_lp'] = data_loader.load_data_profiles(
            self.user_data['data']['paths'],
            self.user_data['data']['local_paths'],
            assumptions.model_yeardays,
            assumptions.model_yeardays_daytype,
            self.user_data['data']['criterias']['plot_tech_lp'])

        # ------------------------
        # Load all SMIF parameters and replace data dict
        # ------------------------
        strategy_variables = self.load_smif_parameters(data_handle)
        assumptions.update('strategy_variables', strategy_variables)

        # Update technologies after strategy definition
        technologies = non_param_assumptions.update_technology_assumption(
            assumptions.technologies,
            assumptions.strategy_variables['f_eff_achieved']['scenario_value'],
            assumptions.strategy_variables['gshp_fraction_ey']['scenario_value'])
        self.user_data['data']['technologies'].update(technologies)

        # Add assumptions to data container
        self.user_data['data']['assumptions'] = assumptions

        # --------------------
        # Initialise scenario
        # --------------------
        self.user_data['init_cont'], self.user_data['data']['fuel_disagg'] = scenario_initalisation(
            self.user_data['data']['data_path'], self.user_data['data'])

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Notes
        -----
        1. Get scenario data

        Population data is required as a nested dict::
            data[year][region_geocode]

        GVA is the same::
            data[year][region_geocode]

        Floor area::
            data[year][region_geoode][sector]

        2. Run initialise scenarios
        3. For each timestep, run the model

        Returns
        =======
        supply_results : dict
            key: name defined in sector models
                value: np.zeros((len(reg), len(intervals)) )
        """
        logging.info("... start simulate() function in wrapper")
        time_start = datetime.datetime.now()

        # ---------------------------------------------
        # Load data from scripts
        # (Get simulation parameters from before_model_run()
        # ---------------------------------------------
        data = self.user_data['data']

        # Set current year
        data['assumptions'].update('curr_yr', data_handle.current_timestep)

        for key, value in self.user_data['init_cont'].items():
            data['assumptions'].update(key, value)

        # Update: Necessary updates after external data definition
        data['technologies']  = non_param_assumptions.update_technology_assumption(
            data['assumptions'].technologies,
            data['assumptions'].strategy_variables['f_eff_achieved']['scenario_value'],
            data['assumptions'].strategy_variables['gshp_fraction_ey']['scenario_value'])

        # --------------------------------------------
        # Load scenario data for base and current year
        # ---------------------------------------------
        data['scenario_data'] = defaultdict(dict)

        pop_array_current = data_handle.get_data('population')  # of simulation year
        gva_array_current = data_handle.get_data('gva')         # of simulation year

        gva_dict_current = {}
        pop_dict_current = {}

        for r_idx, region in enumerate(data['regions']):
            pop_dict_current[region] = pop_array_current[r_idx, 0]
            gva_dict_current[region] = gva_array_current[r_idx, 0]


        data['scenario_data']['population'][data['assumptions'].base_yr] = data['population'][data_handle.base_timestep]
        data['scenario_data']['population'][data['assumptions'].curr_yr] = pop_dict_current

        data['scenario_data']['gva'][data['assumptions'].base_yr] = data['gva'][data_handle.base_timestep]
        data['scenario_data']['gva'][data['assumptions'].curr_yr] = gva_dict_current

        data['scenario_data']['floor_area']['rs_floorarea'] = data['rs_floorarea']
        data['scenario_data']['floor_area']['ss_floorarea'] = data['ss_floorarea']

        #Industry gva
        #data['scenario_data']['gva'][data['assumptions'].curr_yr] = gva_dict_current
        #data['scenario_data']['gva'][data['assumptions'].base_yr] = data['gva'][data_handle.base_timestep]
        #data['scenario_data']['gva'][data['assumptions'].curr_yr] = gva_dict_current

        # ---------------------------------------------
        # Run energy demand model
        # ---------------------------------------------
        sim_obj = energy_demand_model(data, data['assumptions'])

        # ------------------------------------------------
        # Validation base year: Hourly temporal validation
        # ------------------------------------------------
        if data['criterias']['validation_criteria'] == True and data_handle.current_timestep == data['assumptions'].base_yr:
            lad_validation.tempo_spatial_validation(
                data['assumptions'].base_yr,
                data['assumptions'].model_yearhours_nrs,
                data['assumptions'].model_yeardays_nrs,
                data['scenario_data'],
                sim_obj.ed_fueltype_national_yh,
                sim_obj.ed_fueltype_regs_yh,
                data['lookups']['fueltypes'],
                data['lookups']['fueltypes_nr'],
                data['result_paths'],
                data['paths'],
                data['regions'],
                data['reg_coord'],
                data['assumptions'].seasons,
                data['assumptions'].model_yeardays_daytype,
                data['criterias']['plot_crit'])

        # -------------------------------------------
        # Write annual results to txt files
        # -------------------------------------------
        if data['criterias']['write_to_txt']:

            # ---------------------------------------------
            # Create .ini file with simulation info
            # ---------------------------------------------
            write_data.write_simulation_inifile(
                data['result_paths']['data_results'],
                data['enduses'],
                data['assumptions'],
                data['reg_nrs'],
                data['regions'])

            tot_fuel_y_max_enduses = sim_obj.tot_fuel_y_max_enduses
            logging.info("... Start writing results to file")

            # ------------------------
            # Plot individual enduse
            # ------------------------
            if data['criterias']['crit_plot_enduse_lp']:

                # Maybe move to result folder in a later step
                path_folder_lp = os.path.join(data['result_paths']['data_results'], 'individual_enduse_lp')
                basic_functions.delete_folder(path_folder_lp)
                basic_functions.create_folder(path_folder_lp)

                winter_week = list(range(
                    date_prop.date_to_yearday(2015, 1, 12), date_prop.date_to_yearday(2015, 1, 19))) #Jan
                '''spring_week = list(range(
                    date_prop.date_to_yearday(2015, 5, 11), date_prop.date_to_yearday(2015, 5, 18))) #May
                summer_week = list(range(
                    date_prop.date_to_yearday(2015, 7, 13), date_prop.date_to_yearday(2015, 7, 20))) #Jul
                autumn_week = list(range(
                    date_prop.date_to_yearday(2015, 10, 12), date_prop.date_to_yearday(2015, 10, 19))) #Oct'''

                # Plot electricity
                for enduse, ed_yh in sim_obj.tot_fuel_y_enduse_specific_yh.items():
                    plotting_results.plot_enduse_yh(
                        name_fig="individ__electricity_{}_{}".format(enduse, data_handle.current_timestep),
                        path_result=path_folder_lp,
                        ed_yh=ed_yh[data['lookups']['fueltypes']['electricity']],
                        days_to_plot=winter_week)

            write_data.write_supply_results(
                data_handle.current_timestep,
                "result_tot_yh",
                data['result_paths']['data_results_model_runs'],
                sim_obj.ed_fueltype_regs_yh,
                "result_tot_submodels_fueltypes")
            write_data.write_enduse_specific(
                data_handle.current_timestep,
                data['result_paths']['data_results_model_runs'],
                sim_obj.tot_fuel_y_enduse_specific_yh,
                "out_enduse_specific")
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_y",
                [data_handle.current_timestep], sim_obj.reg_load_factor_y, 'reg_load_factor_y')
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_yd",
                [data_handle.current_timestep], sim_obj.reg_load_factor_yd, 'reg_load_factor_yd')
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_winter",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['winter'], 'reg_load_factor_winter')
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_spring",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['spring'], 'reg_load_factor_spring')
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_summer",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['summer'], 'reg_load_factor_summer')
            write_data.write_lf(
                data['result_paths']['data_results_model_runs'], "result_reg_load_factor_autumn",
                [data_handle.current_timestep], sim_obj.reg_seasons_lf['autumn'], 'reg_load_factor_autumn')
            logging.info("... finished writing results to file")

        # ------------------------------------
        # Write results output for supply
        # ------------------------------------
        # Form of np.array (fueltype, sectors, region, periods)
        results_unconstrained = sim_obj.ed_submodel_fueltype_regs_yh

        # Form of {constrained_techs: np.array(fueltype, sectors, region, periods)}
        results_constrained = sim_obj.ed_techs_submodel_fueltype_regs_yh

        #logging.info("dddd" + str(results_unconstrained.shape))

        # --------------------------------------------------------
        # Reshape day and hours to yearhous (from (365, 24) to 8760)
        # --------------------------------------------------------
        supply_sectors = ['residential', 'service', 'industry']

        results_constrained_reshaped = {}
        for heating_tech, submodel_techs in results_constrained.items():
            results_constrained_reshaped[heating_tech] = submodel_techs.reshape(
                len(supply_sectors),
                data['reg_nrs'],
                data['lookups']['fueltypes_nr'],
                8760)
        results_constrained = results_constrained_reshaped

        results_unconstrained = results_unconstrained.reshape(
            len(supply_sectors),
            data['reg_nrs'],
            data['lookups']['fueltypes_nr'],
            8760)

        # -------------------------------------
        # Generate dict for supply model
        # -------------------------------------
        if data['criterias']['mode_constrained']:
            supply_results = constrained_results(
                data['regions'],
                results_constrained,
                results_unconstrained,
                supply_sectors,
                data['lookups']['fueltypes'],
                data['technologies'],
                model_yearhours_nrs=8760)

            '''_sum = 0
            for key, value in supply_results.items():
                logging.info("TEST {}  {}".format(key, np.sum(value)))

                _sum += np.sum(value)
            logging.info("TOTAL SUM in GWh" + str(_sum))'''

            # Generate YAML file with keynames for `sector_model`
            if data['criterias']['writeYAML']:
                write_data.write_yaml_output_keynames(
                    data['local_paths']['yaml_parameters_keynames_constrained'], supply_results.keys())
        else:
            supply_results = unconstrained_results(
                data['regions'],
                results_unconstrained,
                supply_sectors,
                data['lookups']['fueltypes'],
                model_yearhours_nrs=8760)

            # Generate YAML file with keynames for `sector_model`
            if data['criterias']['writeYAML']:
                write_data.write_yaml_output_keynames(
                    data['local_paths']['yaml_parameters_keynames_unconstrained'], supply_results.keys())

        '''_total_scrap = 0
        for key in supply_results:
            _total_scrap += np.sum(supply_results[key])
        print("FINALSUM: " + str(_total_scrap))

        time_end = datetime.datetime.now()
        print("... Total Time: " + str(time_end - time_start))'''

        # ------
        # Write population data of current year to file
        # ------
        write_data.write_scenaric_population_data(
            data_handle.current_timestep,
            data['result_paths']['data_results_model_run_pop'],
            pop_array_current)

        # ------------------------------------
        # Write results to smif
        # ------------------------------------
        if WRITEOUTSMIFRESULTS:
            logging.info("... writing out results to file for smif")
            for key_name, result_to_txt in supply_results.items():
                if key_name in self.outputs.names:
                    data_handle.set_results(
                        key_name,
                        result_to_txt)
                else:
                    raise Exception(
                        "Check running mode (constrained vs unconstrained) as {} is not defined in output".format(
                            key_name))

        logging.info("... finished wrapper execution")
        return supply_results

    def extract_obj(self, results):
        return 0

    def load_smif_parameters(self, data_handle):
        """Get all model parameters from smif (`parameters`) depending
        on narrative. Create the dict `strategy_variables` and
        add scenario value as well as affected enduses of
        each variable.

        Arguments
        ---------
        data_handle : dict
            Data handler

        Returns
        -------
        strategy_variables : dict
            Updated strategy variables
        """
        strategy_variables = {}

        # All information of all scenario parameters
        all_info_scenario_param = param_assumptions.load_param_assump()

        # Get variable from dict and reassign and delete from parameters
        for name in self.parameters.keys():

            # Get scenario value
            scenario_value = data_handle.get_parameter(name)

            if scenario_value == 'True':
                scenario_value = True
            elif scenario_value == 'False':
                scenario_value = False
            else:
                pass

            self.logger.info(
                "Getting parameter: %s value: %s", name, scenario_value)

            strategy_variables[name] = {

                'scenario_value': scenario_value,

                # Get affected enduses of this variable defined in `load_param_assump`
                'affected_enduse': all_info_scenario_param[name]['affected_enduse']}

        return strategy_variables

    def get_long_lat_decimal_degrees(self, reg_centroids):
        """Project coordinates from shapefile to get
        decimal degrees (from OSGB_1936_British_National_Grid to
        WGS 84 projection).

        Arguments
        ---------
        reg_centroids : dict
            Centroid information read in from shapefile via smif

        Return
        -------
        reg_coord : dict
            Contains long and latidue for every region in decimal degrees

        Info
        ----
        http://spatialreference.org/ref/epsg/wgs-84/
        """
        reg_coord = {}
        for centroid in reg_centroids:

            in_projection = Proj(init='epsg:27700') # OSGB_1936_British_National_Grid
            put_projection = Proj(init='epsg:4326') # WGS 84 projection

            # Convert to decimal degrees
            long_dd, lat_dd = transform(
                in_projection,
                put_projection,
                centroid['geometry']['coordinates'][0], #longitude
                centroid['geometry']['coordinates'][1]) #latitude

            reg_coord[centroid['properties']['name']] = {}
            reg_coord[centroid['properties']['name']]['longitude'] = long_dd
            reg_coord[centroid['properties']['name']]['latitude'] = lat_dd

        return reg_coord

def constrained_results(
        regions,
        results_constrained,
        results_unconstrained,
        supply_sectors,
        fueltypes,
        technologies,
        model_yearhours_nrs
    ):
    """Prepare results for energy supply model for
    constrained model running mode (no heat is provided but
    technology specific fuel use).
    The results for the supply model are provided aggregated
    as follows:

        { "submodel_fueltype_tech": np.array(regions, timesteps)}

    Because SMIF only takes results in the
    form of {key: np.array(regions, timesteps)}, the key
    needs to contain information about submodel, fueltype,
    and technology. Also these key must be defined in
    the `submodel_model` configuration file.

    Arguments
    ----------
    regions : dict
        Regions
    results_constrained : dict
        Aggregated results in form
        {technology: np.array((sector, region, fueltype, timestep))}
    results_unconstrained : array
        Restuls of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    supply_sectors : list
        Names of sectors fur supply model
    fueltypes : dict
        Fueltype lookup
    technologies : dict
        Technologies
    model_yearhours_nrs : int
        Number of modelled hours in a year

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}

    Note
    -----
        -   For the fuel demand for CHP plants, the co-generated electricity
            is not included in the demand model. Additional electricity supply
            generated from CHP plants need to be calculated in the supply
            model based on the fuel demand for CHP.
            For CHP efficiency therefore not the overall efficiency is used
            but only the thermal efficiency
    """
    supply_results = {}

    # ----------------------------------------
    # Add all constrained technologies
    # Aggregate according to submodel, fueltype, technology, region, timestep
    # ----------------------------------------
    for submodel_nr, submodel in enumerate(supply_sectors):
        for tech, fuel_tech in results_constrained.items():

            # ----
            # Technological simplifications because of different technology definition
            # and because not all technologies are used in supply model
            # ----
            tech_simplified = model_tech_simplification(tech)
            fueltype_str = technologies[tech].fueltype_str
            fueltype_int = technologies[tech].fueltype_int

            # Generate key name (must be defined in `sector_models`)
            key_name = "{}_{}_{}".format(submodel, fueltype_str, tech_simplified)

            if key_name in supply_results.keys():

                # Iterate over regions and add fuel
                for region_nr, _ in enumerate(regions):
                    supply_results[key_name][region_nr] += fuel_tech[submodel_nr][region_nr][fueltype_int]
            else:
                supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))

                for region_nr, _ in enumerate(regions): #TODO SPEED UP
                    supply_results[key_name][region_nr] = fuel_tech[submodel_nr][region_nr][fueltype_int]

    # --------------------------------
    # Add all technologies of restricted enduse (heating)
    # --------------------------------
    # Calculate tech fueltype specific to fuel of constrained technologies
    constrained_ed  = sum(results_constrained.values())

    # Substract constrained fuel from nonconstrained (total) fuel
    non_heating_ed = results_unconstrained - constrained_ed

    # ---------------------------------
    # Add non_heating for all fueltypes
    # ---------------------------------
    for submodel_nr, submodel in enumerate(supply_sectors):
        for fueltype_str, fueltype_int in fueltypes.items():

            if fueltype_str == 'heat':
                pass #Do not add non_heating demand for fueltype heat
            else:
                # Generate key name (must be defined in `sector_models`)
                key_name = "{}_{}_{}".format(
                    submodel, fueltype_str, "non_heating")

                # Iterate regions and add fuel #TODO SPEED UP
                supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))
                for region_nr, _ in enumerate(regions):
                    supply_results[key_name][region_nr] = non_heating_ed[submodel_nr][region_nr][fueltype_int]

    # --------------------------------------------
    # Check whether any entry is smaller than zero
    # --------------------------------------------
    for key, key_data in supply_results.items():
        for reg_data in key_data:
            for hour in reg_data:
                if hour < 0:
                    raise Exception("Minus value is provided as output {}".format(key))

    logging.info("... Prepared results for energy supply model in constrained mode")
    return supply_results

def unconstrained_results(
        regions,
        results_unconstrained,
        supply_sectors,
        fueltypes,
        model_yearhours_nrs
    ):
    """Prepare results for energy supply model for
    unconstrained model running mode (heat is provided).
    The results for the supply model are provided aggregated
    for every submodel, fueltype, region, timestep

    Note
    -----
    Because SMIF only takes results in the
    form of {key: np.aray(regions, timesteps)}, the key
    needs to contain information about submodel and fueltype

    Also these key must be defined in the `submodel_model`
    configuration file

    Arguments
    ----------
    regions : dict
        Regions
    results_unconstrained : array
        Results of unconstrained mode
        np.array((sector, regions, fueltype, timestep))
    supply_sectors : list
        Names of sectors for supply model
    fueltypes : dict
        Fueltype lookup
    model_yearhours_nrs : int
        Number of modelled hours in a year

    Returns
    -------
    supply_results : dict
        No technology specific delivery (heat is provided in form of a fueltype)
        {submodel_fueltype: np.array((region, intervals))}
    """
    supply_results = {}

    # Iterate submodel and fueltypes
    for submodel_nr, submodel in enumerate(supply_sectors):
        for fueltype_str, fueltype_int in fueltypes.items():

            # Generate key name (must be defined in `sector_models`)
            key_name = "{}_{}".format(submodel, fueltype_str)

            supply_results[key_name] = np.zeros((len(regions), model_yearhours_nrs))

            for region_nr, _ in enumerate(regions):
                supply_results[key_name][region_nr] = results_unconstrained[submodel_nr][region_nr][fueltype_int]

    logging.info("... Prepared results for energy supply model in unconstrained mode")
    return supply_results

def model_tech_simplification(tech):
    """This function aggregated different technologies
    which are not defined in supply model

    Arguments
    ---------
    tech : str
        Technology

    Returns
    -------
    tech_newly_assigned : str
        Technology newly assigned
    """
    # Assign condensing boiler to regular boilers
    if tech == 'boiler_condensing_gas':
        tech_newly_assigned = 'boiler_gas'
    elif tech == 'boiler_condensing_oil':
        tech_newly_assigned = 'boiler_oil'
    elif tech == 'storage_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    elif tech == 'secondary_heater_electricity':
        tech_newly_assigned = 'boiler_electricity'
    else:
        tech_newly_assigned = tech

    return tech_newly_assigned
