"""Digital demand dummy model
"""
import configparser
import csv
import os

from digital_comms.mobile_network.model import NetworkManager
from smif.model import SectorModel

class DigitalMobileWrapper(SectorModel):

    def simulate(self, data_handle):
        self.logger.debug("Running {} timestep {}".format(self.__class__, data_handle.current_timestep))

        self.logger.debug("INPUTS")
        self.logger.debug(self.inputs)
        self.logger.debug(self.parameters)

        #load list of lads
        # lads = []
        # lad_shapes = os.path.join(
        #     SHAPES_INPUT_PATH, 'lad_uk_2016-12', 'lad_uk_2016-12.shp'
        #     )
        # with fiona.open(lad_shapes, 'r') as lad_shape:
        #     for lad in lad_shape:
        #         if not lad['properties']['name'].startswith((
        #             'E06000053',
        #             'S12000027',
        #             'N09000001',
        #             'N09000002',
        #             'N09000003',
        #             'N09000004',
        #             'N09000005',
        #             'N09000006',
        #             'N09000007',
        #             'N09000008',
        #             'N09000009',
        #             'N09000010',
        #             'N09000011',
        #             )):
        #             lads.append({
        #                 "id": lad['properties']['name'],
        #                 "name": lad['properties']['desc'],
        #             })

        # 'id' | 'name'
        #

        #load population scenario
        current_population = data_handle.get_data("population").as_df().reset_index()
        # print(current_population.head())
        # postcode_sector | population
        # AB1 A | 123

        #load data growth scenario data
        current_data_demand = data_handle.get_data("data_growth").as_df().reset_index()
        # year | index | data_growth
        # 0 | 0 | 0.8

        #load parameters
        read_only_parameters = data_handle.get_parameters()
        parameters = {}
        for name, data_array in read_only_parameters.items():
            parameters[name] = float(data_array.data)

        # for pcd_sector in pcd_sectors:
        #     try:
        #         pcd_sector_id = pcd_sector["id"]
        #         pcd_sector["population"] = (
        #             population_by_scenario_year_pcd \
        #                 [pop_scenario][year][pcd_sector_id])
        #         pcd_sector["user_throughput"] = (
        #             user_throughput_by_scenario_year \
        #                 [throughput_scenario][year])
        #     except:
        #         pass

        # Run model
        # system = NetworkManager(
        #     lads,
        #     pcd_sectors,
        #     assets,
        #     capacity_lookup_table,
        #     clutter_lookup,
        #     simulation_parameters
        # )

        # Write outputs
        # write_lad_results(system, folder, year, pop_scenario, throughput_scenario,
        #     intervention_strategy, cost_by_lad)
        # write_pcd_results(system, folder, year, pop_scenario, throughput_scenario,
        #     intervention_strategy, cost_by_pcd)
