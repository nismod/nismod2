"""Energy supply wrapper
"""
import numpy as np
from smif.model.sector_model import SectorModel


class EnergySupplyWrapper(SectorModel):
    """Energy supply
    """
    def initialise(self, initial_conditions):
        pass

    def simulate(self, data):

        # Get the current timestep
        now = data.current_timestep
        self.logger.info("Energy supplyWrapper received inputs in %s", now)

        # Get model parameters
        parameter_LoadShed_elec = data.get_parameter('LoadShed_elec')
        self.logger.info('Parameter Loadshed elec: %s', parameter_LoadShed_elec)
        
        parameter_LoadShed_gas = data.get_parameter('LoadShed_gas')
        self.logger.info('Parameter Loadshed gas: %s', parameter_LoadShed_gas)
        
        # Get model inputs
        input_residential_gas_boiler_gas = data.get_data("residential_gas_boiler_gas")
        self.logger.info('Input Residential gas boiler gas: %s', 
            input_residential_gas_boiler_gas)
        
        input_residential_electricity_boiler_electricity = data.get_data("residential_electricity_boiler_electricity")
        self.logger.info('Input Residential electricity boiler electricity: %s', 
            input_residential_electricity_boiler_electricity)
    
        input_gas_price = data.get_data("gas_price")
        self.logger.info('Input Gas price: %s', input_gas_price)

        heatload_eh_inputs = np.array(
            input_residential_gas_boiler_gas,
            input_residential_electricity_boiler_electricity
            )

        heatload_eh = np.sum.reduce(heatload_eh_inputs, axis=1)

        # Write results to data handler
        data.set_results("emissions_elec", None)

        self.logger.info("Energy supplyWrapper produced outputs in %s", now)

    def extract_obj(self, results):
        return 0