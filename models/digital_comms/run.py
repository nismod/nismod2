"""Digital demand dummy model
"""
import configparser
import csv
import os

#from memory_profiler import profile
#from pyinstrument import Profiler

import fiona
import numpy as np

from digital_comms.fixed_network.model import ICTManager
from digital_comms.fixed_network.interventions import decide_interventions
from digital_comms.fixed_network.adoption import update_adoption_desirability

from smif.model.sector_model import SectorModel

# numpy options
np.set_printoptions(threshold=np.nan)

# configure profiling with environment variable
PROFILE = False
if 'PROFILE_DC' in os.environ and os.environ['PROFILE_DC'] == "1":
    PROFILE = True


def memprofile(func):
    """Decorator - profile memory usage if profiling is enabled
    """
    def wrapper(*args, **kwargs):
        if PROFILE:
            profile(func, precision=1)(*args, **kwargs)
        else:
            func(*args, **kwargs)
    return wrapper


def cpuprofile(func):
    """Decorator - profile cpu usage
    """
    def wrapper(*args, **kwargs):
        if PROFILE:
            profiler = Profiler()
            profiler.start()
        func(*args, **kwargs)
        if PROFILE:
            profiler.stop()
            print(profiler.output_text(unicode=False, color=True))
    return wrapper


class DigitalCommsWrapper(SectorModel):
    """Digital model
    """
    def __init__(self, name):
        super().__init__(name)

        self.user_data = {}

    def initialise(self, initial_conditions):
        print('initialise')

    @cpuprofile
    @memprofile
    def before_model_run(self, data_handle):
        print('before model run')
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)
        """

        # Get wrapper configuration
        path_main = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(path_main, 'wrapperconfig.ini'))
        data_path = config['PATHS']['path_local_data']

        # Get modelrun configuration
        parameters = data_handle.get_parameters()
        parameters = {parameter: int(parameters[parameter].as_ndarray()) for parameter in parameters}

        # Get strategy
        if parameters['technology_strategy'] == 0:
            parameters['technology_strategy'] = 'fttdp_subsidised_rollout_per_distribution'

        # Load assets
        assets = {}
        assets['premises'] = read_shapefile(os.path.join(data_path, 'assets_layer5_premises.shp'))
        assets['distributions'] = read_shapefile(os.path.join(data_path, 'assets_layer4_distributions.shp'))
        assets['cabinets'] = read_shapefile(os.path.join(data_path, 'assets_layer3_cabinets.shp'))
        assets['exchanges'] = read_shapefile(os.path.join(data_path, 'assets_layer2_exchanges.shp'))

        # Load links
        links = []
        links.extend(read_shapefile(os.path.join(data_path, 'links_layer5_premises.shp')))
        links.extend(read_shapefile(os.path.join(data_path, 'links_layer4_distributions.shp')))
        links.extend(read_shapefile(os.path.join(data_path, 'links_layer3_cabinets.shp')))

        self.logger.info("DigitalCommsWrapper - Intitialise system")
        self.system = ICTManager(assets, links, parameters)

        print('only distribution points with a benefit cost ratio > 1 can be upgraded')
        print('model rollout is constrained by the adoption desirability set by scenario')


    @cpuprofile
    @memprofile
    def simulate(self, data_handle):
        # -----
        # Start
        # -----
        now = data_handle.current_timestep
        self.logger.info("DigitalCommsWrapper received inputs in %s", now)

        # Set global parameters
        STRATEGY = int(data_handle.get_parameter('technology_strategy').as_ndarray())
        if STRATEGY == 0:
            STRATEGY = 'fttdp_subsidised_rollout_per_distribution'

        TECH = STRATEGY.split("_")[0]

        # -----------------------
        # Get scenario adoption rate
        # -----------------------
        print("-------------------")
        print("Running", TECH, STRATEGY, data_handle.current_timestep)
        print("-------------------")
        annual_adoption_rate = data_handle.get_data('adoption').data[0]
        adoption_desirability = [premise for premise in self.system._premises if premise.adoption_desirability is True]
        total_premises = [premise for premise in self.system._premises]
        adoption_desirability_percentage = (len(adoption_desirability) / len(total_premises) * 100)
        percentage_annual_increase = annual_adoption_rate - adoption_desirability_percentage
        percentage_annual_increase = round(float(percentage_annual_increase), 1)
        print("* {} annual_adoption_rate is {} %".format(TECH, percentage_annual_increase))

        # -----------------------
        # Run fixed network model
        # -----------------------
        self.logger.info("DigitalCommsWrapper - Update adoption status on premises")
        self.system.update_adoption_desirability = update_adoption_desirability(self.system, percentage_annual_increase)
        premises_adoption_desirability_ids = self.system.update_adoption_desirability
        
        MAXIMUM_ADOPTION = len(premises_adoption_desirability_ids) + sum(getattr(premise, TECH) for premise in self.system._premises)
        # print("// length of premises_adoption_desirability_ids is {}".format(len(premises_adoption_desirability_ids)+1))
        # print("// sum of premises by tech {}".format(sum(getattr(premise, TECH) for premise in self.system._premises)))
        # print("// MAXIMUM_ADOPTION is {}".format(MAXIMUM_ADOPTION))

        self.logger.info("DigitalCommsWrapper - Decide interventions")
        interventions, budget, spend, match_funding_spend, subsidised_spend = decide_interventions(
            STRATEGY, int(data_handle.get_parameter('annual_budget').data), int(data_handle.get_parameter('service_obligation_capacity').data), 
            self.system, now, MAXIMUM_ADOPTION, int(data_handle.get_parameter('telco_match_funding').data), 
            int(data_handle.get_parameter('subsidy').data))

        self.logger.info("DigitalCommsWrapper - Upgrading system")
        self.system.upgrade(interventions)

        # -------------
        # Write outputs
        # -------------
        interventions_lut = {intervention[0]:intervention for intervention in interventions}

        distribution_upgrades = np.empty((self.system.number_of_assets['distributions'],1))
        for idx, distribution in enumerate(self.outputs['distribution_upgrades'].dim_coords('broadband_distributions').ids):
            distribution_upgrades[idx, 0] = interventions_lut[distribution][2] if distribution in interventions_lut else 0
        data_handle.set_results('distribution_upgrades', distribution_upgrades)

        premises_by_distribution = np.empty((self.system.number_of_assets['distributions'],1))
        for idx, distribution in enumerate(self.system.assets['distributions']):
            premises_by_distribution[idx, 0] = len(distribution._clients)
        data_handle.set_results('premises_by_distribution', premises_by_distribution)

        print("* {} premises adoption desirability is {}".format(TECH, (len(premises_adoption_desirability_ids))))
        premises_wanting_to_adopt = np.empty((1,1))
        premises_wanting_to_adopt[0, 0] = len(premises_adoption_desirability_ids)
        data_handle.set_results('premises_adoption_desirability', premises_wanting_to_adopt)

        if TECH == 'fttp':

            distribution_upgrade_costs_fttp = np.empty((self.system.number_of_assets['distributions'],1))
            for idx, distribution in enumerate(self.system.assets['distributions']):
                distribution_upgrade_costs_fttp[idx, 0] = distribution.upgrade_costs['fttp']
            data_handle.set_results('distribution_upgrade_costs_fttp', distribution_upgrade_costs_fttp)

            upgrade_cost_per_premises_fttp = np.empty((self.system.number_of_assets['distributions'],1))
            for idx, distribution in enumerate(self.system.assets['distributions']):
                if len(distribution._clients) > 0:
                    upgrade_cost_per_premises_fttp[idx, 0] = distribution.upgrade_costs['fttp'] / len(distribution._clients)
                else:
                    upgrade_cost_per_premises_fttp[idx, 0] = 0
            data_handle.set_results('premises_upgrade_costs_fttp', upgrade_cost_per_premises_fttp)

            premises_passed_with_fttp = np.empty((1,1))
            premises_passed_with_fttp[0, 0] = sum(premise.fttp for premise in self.system._premises) 
            print("* fttp premises passed {}".format(premises_passed_with_fttp))
            data_handle.set_results('premises_passed_with_fttp', premises_passed_with_fttp)

            percentage_of_premises_passed_with_fttp = np.empty((1,1))
            percentage_of_premises_passed_with_fttp[0, 0] = round((sum(premise.fttp for premise in self.system._premises) / len(self.system._premises)*100),2)
            print("* fttp % premises passed {}".format(percentage_of_premises_passed_with_fttp))
            data_handle.set_results('percentage_of_premises_passed_with_fttp', percentage_of_premises_passed_with_fttp)

            premises_connected_with_fttp = np.empty((1,1))
            premises_connected_with_fttp[0, 0] = sum(premise.fttp for premise in self.system._premises if premise.adoption_desirability == True) 
            print("* fttp premises connected {}".format(premises_connected_with_fttp))
            data_handle.set_results('premises_connected_with_fttp', premises_connected_with_fttp)

            percentage_of_premises_connected_with_fttp = np.empty((1,1))
            percentage_of_premises_connected_with_fttp[0, 0] = round((sum(premise.fttp for premise in self.system._premises if premise.adoption_desirability == True) / len(self.system._premises)*100),2)
            print("* fttp % premises connected {}".format(percentage_of_premises_connected_with_fttp))
            data_handle.set_results('percentage_of_premises_connected_with_fttp', percentage_of_premises_connected_with_fttp)

        if TECH == 'fttdp':

            distribution_upgrade_costs_fttdp = np.empty((self.system.number_of_assets['distributions'],1))
            for idx, distribution in enumerate(self.system.assets['distributions']):
                distribution_upgrade_costs_fttdp[idx, 0] = distribution.upgrade_costs['fttdp']
            data_handle.set_results('distribution_upgrade_costs_fttdp', distribution_upgrade_costs_fttdp)

            upgrade_cost_per_premises_fttdp = np.empty((self.system.number_of_assets['distributions'],1))
            for idx, distribution in enumerate(self.system.assets['distributions']):
                if len(distribution._clients) > 0:
                    upgrade_cost_per_premises_fttdp[idx, 0] = distribution.upgrade_costs['fttdp'] / len(distribution._clients)
                else:
                    upgrade_cost_per_premises_fttdp[idx, 0] = 0
            data_handle.set_results('premises_upgrade_costs_fttdp', upgrade_cost_per_premises_fttdp)

            # premises_with_fttdp = np.empty((1,1))
            # premises_with_fttdp[0, 0] = sum(premise.fttdp for premise in self.system._premises)
            # print("* fttdp premises passed {}".format(premises_with_fttdp))
            # data_handle.set_results('premises_with_fttdp', premises_with_fttdp)

            premises_passed_with_fttdp = np.empty((1,1))
            premises_passed_with_fttdp[0, 0] = sum(premise.fttdp for premise in self.system._premises) 
            print("* fttdp premises passed {}".format(premises_passed_with_fttdp))
            data_handle.set_results('premises_passed_with_fttdp', premises_passed_with_fttdp)
            
            # percentage_of_premises_with_fttdp = np.empty((1,1))
            # percentage_of_premises_with_fttdp[0, 0] = round((sum(premise.fttdp for premise in self.system._premises) / len(self.system._premises)*100),2)
            # print("* fttdp % premises passed {}".format(percentage_of_premises_with_fttdp))
            # data_handle.set_results('premises_with_fttdp', percentage_of_premises_with_fttdp)

            percentage_of_premises_passed_with_fttdp = np.empty((1,1))
            percentage_of_premises_passed_with_fttdp[0, 0] = round((sum(premise.fttdp for premise in self.system._premises) / len(self.system._premises)*100),2)
            print("* fttdp % premises passed {}".format(percentage_of_premises_passed_with_fttdp))
            data_handle.set_results('percentage_of_premises_passed_with_fttdp', percentage_of_premises_passed_with_fttdp)

            premises_connected_with_fttdp = np.empty((1,1))
            premises_connected_with_fttdp[0, 0] = sum(premise.fttdp for premise in self.system._premises if premise.adoption_desirability == True) 
            print("* fttdp premises connected {}".format(premises_connected_with_fttdp))
            data_handle.set_results('premises_connected_with_fttdp', premises_connected_with_fttdp)

            percentage_of_premises_connected_with_fttdp = np.empty((1,1))
            percentage_of_premises_connected_with_fttdp[0, 0] = round((sum(premise.fttdp for premise in self.system._premises if premise.adoption_desirability == True) / len(self.system._premises)*100),2)
            print("* fttdp % premises connected {}".format(percentage_of_premises_connected_with_fttdp))
            data_handle.set_results('percentage_of_premises_connected_with_fttdp', percentage_of_premises_connected_with_fttdp)

        # Regional output

        lad_names = self.outputs['lad_premises_with_fttp'].dim_coords('lad_uk_2016').ids
        num_lads = len(lad_names)
        num_fttp = np.zeros((num_lads, 1))
        num_fttdp = np.zeros((num_lads, 1))
        num_fttc = np.zeros((num_lads, 1))
        num_adsl = np.zeros((num_lads, 1))

        coverage = self.system.coverage()
        for i, lad in enumerate(lad_names):
            if lad not in coverage:
                continue
            stats = coverage[lad]
            num_fttp[i, 0] = stats['num_fttp']
            num_fttdp[i, 0] = stats['num_fttdp']
            num_fttc[i, 0] = stats['num_fttc']
            num_adsl[i, 0] = stats['num_adsl']

        data_handle.set_results('lad_premises_with_fttp', num_fttp)
        data_handle.set_results('lad_premises_with_fttdp', num_fttdp)
        # data_handle.set_results('lad_premises_with_fttc', num_fttc)
        # data_handle.set_results('lad_premises_with_adsl', num_adsl)

        # ----
        # Exit
        # ----
        self.logger.info("DigitalCommsWrapper produced outputs in %s",
                         now)

    def extract_obj(self, results):
        return 0

def read_shapefile(file):
    with fiona.open(file, 'r') as source:
        return [f['properties'] for f in source]
