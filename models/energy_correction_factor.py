"""Apply correction factors to energy_demand_unconstrained outputs
"""
from smif.exception import SmifException
from smif.model import SectorModel


class EnergyCorrectionFactor(SectorModel):
    """Adaptor to apply energy correction factors
    """
    def simulate(self, data_handle):
        """Read inputs, apply factor, write out.
        """
        # Conversions to apply
        # - fuel: gas or electricity
        # - service: service or technology grouping
        # - factor: correction factor to apply
        # - inputs: list of inputs (all have the same factor applied)
        conversions = [
            {
                'fuel': 'electricity',
                'service': 'boiler',
                'factor': 0.9,
                'inputs': [
                    'residential_electricity_boiler_electricity',
                    'industry_electricity_boiler_electricity',
                    'service_electricity_boiler_electricity'
                ]
            },
            {
                'fuel': 'electricity',
                'service': 'heat_pump',
                'factor': 1.5,
                'inputs': [
                    'residential_electricity_heat_pumps_electricity',
                    'industry_electricity_heat_pumps_electricity',
                    'service_electricity_heat_pumps_electricity'
                ]
            },
            {
                'fuel': 'electricity',
                'service': 'dh',
                'factor': 0.9,
                'inputs': [
                    'residential_electricity_district_heating_electricity',
                    'industry_electricity_district_heating_electricity',
                    'service_electricity_district_heating_electricity'
                ]
            },
            {
                'fuel': 'electricity',
                'service': 'non_heating',
                'factor': 0.9,
                'inputs': [
                    'residential_electricity_non_heating',
                    'industry_electricity_non_heating',
                    'service_electricity_non_heating',
                    'residential_electricity',
                    'industry_electricity',
                    'service_electricity'
                ],
            },
            {
                'fuel': 'gas',
                'service': 'boiler',
                'factor': 0.8,
                'inputs': [
                    'industry_gas_boiler_gas',
                    'service_gas_boiler_gas',
                    'residential_gas_boiler_gas'
                ]
                },
            {
                'fuel': 'gas',
                'service': 'dh_chp',
                'factor': 0.5,
                'inputs': [
                    'residential_gas_district_heating_CHP_gas',
                    'industry_gas_district_heating_CHP_gas',
                    'service_gas_district_heating_CHP_gas'
                ]
                },
            {
                'fuel': 'gas',
                'service': 'non_heating',
                'factor': 0.7,
                'inputs': [
                    'residential_gas_non_heating',
                    'industry_gas_non_heating',
                    'service_gas_non_heating',
                    'residential_gas',
                    'industry_gas',
                    'service_gas'
                ]
            }
        ]

        for conversion in conversions:
            for input_name in conversion['inputs']:
                if input_name in self.inputs:
                    self._check_output_exists(input_name)
                    data = data_handle.get_data(input_name).as_ndarray()
                    # divide by factor
                    results = data / conversion['factor']
                    data_handle.set_results(input_name, results)
                else:
                    self.logger.warning(
                        "No input found for {}, skipping correction factor".format(input_name))

    def _check_output_exists(self, input_name):
        try:
            model_output = self.outputs[input_name]
        except KeyError:
            msg = "Output '{}' not found to match input '{}' in model '{}'".format(
                input_name, model_input, self.name)
            raise SmifException(msg)
