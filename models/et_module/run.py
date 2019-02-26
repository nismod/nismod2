"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
import configparser
import numpy as np

from et_module.main import main

REGION_SET_NAME = 'lad_uk_2016'

class ETWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)
        self.user_data = {}

    def array_to_dict(self, input_array):
        """Convert array to dict

        Arguments
        ---------
        input_array : numpy.ndarray
            timesteps, regions, interval

        Returns
        -------
        output_dict : dict
            timesteps, region, interval

        """
        output_dict = defaultdict(dict)
        for r_idx, region in enumerate(self.get_region_names(REGION_SET_NAME)):
            output_dict[region] = input_array[r_idx, 0]

        return dict(output_dict)

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

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : dict
            A dictionary containing all parameters and model inputs defined in
            the smif configuration by name

        Returns
        =======
        et_module_out : dict
            Outputs of et_module
        """
        regions = data_handle.get_region_names(REGION_SET_NAME)

        simulation_yr = data_handle.current_timestep

        # Read number of EV trips starting in regions (np.array(regions, 24h))
        reg_trips_ev_24h = data_handle.get_data('trips')

        # Get hourly demand data for day for every region (np.array(regions, 24h)) (kWh)
        reg_elec_24h = data_handle.get_data('electricity')

        actual_v2g_capacity = main(regions, 
                                   simulation_yr, 
                                   reg_trips_ev_24h, 
                                   reg_elec_24h)

        data_handle.set_results('capacity', actual_v2g_capacity)

    def extract_obj(self, results):
        return 0