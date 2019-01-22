from models.energy_supply.energy_supply import EnergySupplyWrapper, write_input_timestep

class EnergySupplyToyWrapper(EnergySupplyWrapper):
    """Monkey patches methods in full version of wrapper with minimal dimension
    definitions
    """

    def get_names(self, name, spatial_name='energy_hub_min', temporal_name='seasonal_week'):
        """Get region and interval names for a given input
        """
        return super().get_names(name, spatial_name, temporal_name)

    def get_gasload(self, data, now):
        gasload = data.get_data('gasload')
        region_names, interval_names = self.get_names("gasload", spatial_name='gas_nodes_minimal')
        self.logger.debug('Writing %s to database', "gasload")
        write_input_timestep(gasload, "gasload", now, region_names, interval_names)