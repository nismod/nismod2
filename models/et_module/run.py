"""The sector model wrapper for smif to run the energy demand model
"""
from smif.model import SectorModel
from et_module.main import main

REGION_SET_NAME = 'lad_gb_2016'

class ETWrapper(SectorModel):
    """Energy-Transport Model Wrapper
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
        simulation_yr = data_handle.current_timestep

        # Read number of EV trips starting in regions (np.array(regions, 24h))
        reg_trips_ev_24h = data_handle.get_data('ev_trips')
        
        # Obtain the list of regions from the model input
        regions = reg_trips_ev_24h.dim_coords(REGION_SET_NAME).ids

        # Get hourly demand data for day for every region (np.array(regions, 24h)) (kWh)
        reg_elec_24h = data_handle.get_data('ev_electricity')

        actual_v2g_capacity = main(regions, 
                                   simulation_yr, 
                                   reg_trips_ev_24h.as_ndarray(), 
                                   reg_elec_24h.as_ndarray())

        data_handle.set_results('v2g_g2v_capacity', actual_v2g_capacity)
