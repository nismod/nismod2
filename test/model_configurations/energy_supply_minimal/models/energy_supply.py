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
        
        input_residential_gas_stirling_micro_CHP = data.get_data("residential_gas_stirling_micro_CHP")
        self.logger.info('Input Residential gas stirling micro chp: %s', input_residential_gas_stirling_micro_CHP)
        
        input_residential_electricity_heat_pumps_electricity = data.get_data("residential_electricity_heat_pumps_electricity")
        self.logger.info('Input Residential electricity heat pumps electricity: %s', input_residential_electricity_heat_pumps_electricity)
        
        input_residential_electricity_district_heating_electricity = data.get_data("residential_electricity_district_heating_electricity")
        self.logger.info('Input Residential electricity district heating electricity: %s', input_residential_electricity_district_heating_electricity)
        input_residential_gas_district_heating_gas = data.get_data("residential_gas_district_heating_gas")
        self.logger.info('Input Residential gas district heating gas: %s', input_residential_gas_district_heating_gas)
        input_residential_gas_non_heating = data.get_data("residential_gas_non_heating")
        self.logger.info('Input Residential gas non heating: %s', input_residential_gas_non_heating)
        input_residential_electricity_non_heating = data.get_data("residential_electricity_non_heating")
        self.logger.info('Input Residential electricity non heating: %s', input_residential_electricity_non_heating)
        input_service_gas_boiler_gas = data.get_data("service_gas_boiler_gas")
        self.logger.info('Input Service gas boiler gas: %s', input_service_gas_boiler_gas)
        input_service_electricity_boiler_electricity = data.get_data("service_electricity_boiler_electricity")
        self.logger.info('Input Service electricity boiler electricity: %s', input_service_electricity_boiler_electricity)
        input_service_gas_stirling_micro_CHP = data.get_data("service_gas_stirling_micro_CHP")
        self.logger.info('Input Service gas stirling micro chp: %s', input_service_gas_stirling_micro_CHP)
        input_service_electricity_heat_pumps_electricity = data.get_data("service_electricity_heat_pumps_electricity")
        self.logger.info('Input Service electricity heat pumps electricity: %s', input_service_electricity_heat_pumps_electricity)
        input_service_electricity_district_heating_electricity = data.get_data("service_electricity_district_heating_electricity")
        self.logger.info('Input Service electricity district heating electricity: %s', input_service_electricity_district_heating_electricity)
        input_service_gas_district_heating_gas = data.get_data("service_gas_district_heating_gas")
        self.logger.info('Input Service gas district heating gas: %s', input_service_gas_district_heating_gas)
        input_service_gas_non_heating = data.get_data("service_gas_non_heating")
        self.logger.info('Input Service gas non heating: %s', input_service_gas_non_heating)
        input_service_electricity_non_heating = data.get_data("service_electricity_non_heating")
        self.logger.info('Input Service electricity non heating: %s', input_service_electricity_non_heating)
        input_industry_gas_boiler_gas = data.get_data("industry_gas_boiler_gas")
        self.logger.info('Input Industry gas boiler gas: %s', input_industry_gas_boiler_gas)
        input_industry_electricity_boiler_electricity = data.get_data("industry_electricity_boiler_electricity")
        self.logger.info('Input Industry electricity boiler electricity: %s', input_industry_electricity_boiler_electricity)
        input_industry_biomass_boiler_biomass = data.get_data("industry_biomass_boiler_biomass")
        self.logger.info('Input Industry biomass boiler biomass: %s', input_industry_biomass_boiler_biomass)
        input_industry_gas_stirling_micro_CHP = data.get_data("industry_gas_stirling_micro_CHP")
        self.logger.info('Input Industry gas stirling micro chp: %s', input_industry_gas_stirling_micro_CHP)
        input_industry_electricity_heat_pumps_electricity = data.get_data("industry_electricity_heat_pumps_electricity")
        self.logger.info('Input Industry electricity heat pumps electricity: %s', input_industry_electricity_heat_pumps_electricity)
        input_industry_electricity_district_heating_electricity = data.get_data("industry_electricity_district_heating_electricity")
        self.logger.info('Input Industry electricity district heating electricity: %s', input_industry_electricity_district_heating_electricity)
        input_industry_gas_district_heating_gas = data.get_data("industry_gas_district_heating_gas")
        self.logger.info('Input Industry gas district heating gas: %s', input_industry_gas_district_heating_gas)
        input_industry_biomass_district_heating_biomass = data.get_data("industry_biomass_district_heating_biomass")
        self.logger.info('Input Industry biomass district heating biomass: %s', input_industry_biomass_district_heating_biomass)
        input_industry_gas_non_heating = data.get_data("industry_gas_non_heating")
        self.logger.info('Input Industry gas non heating: %s', input_industry_gas_non_heating)
        input_industry_electricity_non_heating = data.get_data("industry_electricity_non_heating")
        self.logger.info('Input Industry electricity non heating: %s', input_industry_electricity_non_heating)
        input_cost_of_carbon = data.get_data("cost_of_carbon")
        self.logger.info('Input Cost of carbon: %s', input_cost_of_carbon)
        input_electricity_price = data.get_data("electricity_price")
        self.logger.info('Input Electricity price: %s', input_electricity_price)
        input_gas_price = data.get_data("gas_price")
        self.logger.info('Input Gas price: %s', input_gas_price)
        input_nuclearFuel_price = data.get_data("nuclearFuel_price")
        self.logger.info('Input Nuclearfuel price: %s', input_nuclearFuel_price)
        input_oil_price = data.get_data("oil_price")
        self.logger.info('Input Oil price: %s', input_oil_price)
        input_coal_price = data.get_data("coal_price")
        self.logger.info('Input Coal price: %s', input_coal_price)
        
        # Write results to data handler
        data.set_results("gasfired_gen_tran", None)
        data.set_results("coal_gen_tran", None)
        data.set_results("hydro_gen_tran", None)
        data.set_results("pumpedHydro_gen_tran", None)
        data.set_results("nuclear_gen_tran", None)
        data.set_results("interconnector_elec_tran", None)
        data.set_results("renewable_gen_tran", None)
        data.set_results("wind_gen_tran", None)
        data.set_results("pv_gen_tran", None)
        data.set_results("wind_curtail_tran", None)
        data.set_results("pv_curtail_tran", None)
        data.set_results("gasfired_gen_eh", None)
        data.set_results("wind_gen_eh", None)
        data.set_results("pv_gen_eh", None)
        data.set_results("lng_supply", None)
        data.set_results("domestic_gas", None)
        data.set_results("interconnector_gas", None)
        data.set_results("storage_gas", None)
        data.set_results("load_shed_gas", None)
        data.set_results("load_shed_elec", None)
        data.set_results("emissions_elec", None)
        data.set_results("elec_cost", None)
        data.set_results("heat_gasboiler", None)
        data.set_results("heat_heatpump", None)
        data.set_results("elec_reserve_tran", None)
        data.set_results("problem_objective", None)
        data.set_results("problem_status", None)
        data.set_results("total_opt_cost", None)
        
        self.logger.info("Energy supplyWrapper produced outputs in %s", now)

    def extract_obj(self, results):
        return 0