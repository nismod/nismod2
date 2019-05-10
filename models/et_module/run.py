"""The sector model wrapper for smif to run the energy demand model
"""
from smif.model import SectorModel
from et_module.main import main

REGION_SET_NAME = 'lad_gb_2016'

class ETWrapper(SectorModel):
    """Energy-Transport Model Wrapper
    """
    def before_model_run(self, data):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data: smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)
        """

    def simulate(self, data):
        """Runs the model for one `timestep`

        Arguments
        ---------
        data : smif.data_layer.DataHandle
            Access all parameters and model inputs defined in the smif configuration by name
        """
        simulation_yr = data.current_timestep

        # Read number of EV trips starting
        reg_trips_ev_24h = data.get_data('ev_trips').as_ndarray()

        # Get hourly demand data for day for every region (kWh)
        reg_elec_24h = data.get_data('ev_electricity').as_ndarray()

        # Obtain the list of regions from the model input
        regions = self.inputs['ev_trips'].dim_coords(REGION_SET_NAME).ids

        actual_v2g_capacity = main(regions, simulation_yr, reg_trips_ev_24h, reg_elec_24h)

        data.set_results('v2g_g2v_capacity', actual_v2g_capacity)
