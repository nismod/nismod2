"""This adapter aggregates all inputs and writes the aggregate
values to each output
"""
import numpy as np
from smif.model import SectorModel


class AggregateInputs(SectorModel):
    """An Adapter to aggregate all inputs

    Outputs the same aggregate to each output.
    """
    def simulate(self, data_handle):
        """Aggregates inputs to output
        """
        inputs = []
        for input_name in self.inputs.keys():
            self.logger.debug("Model input: %s", input_name)
            inputs.append(data_handle.get_data(input_name).as_ndarray())

        data_array = np.array(inputs)
        aggregate_data = np.add.reduce(data_array, axis=0)

        for output_name in self.outputs.keys():
            data_handle.set_results(output_name, aggregate_data)

class AggregateEnergyConstrained(SectorModel):
    """Aggregate inputs to outputs for energy models in constrained heat mode
    """
    def simulate(self, data_handle):
        to_output_from_inputs = self._get_aggregate_map()

        for output_name, input_names in to_output_from_inputs.items():
            assert output_name in self.outputs, \
                "Expected to find output '{}' when aggregating".format(output_name)
            output_spec = self.outputs[output_name]
            output_data = np.zeros(output_spec.shape)

            for input_name in input_names:
                assert input_name in self.inputs, \
                    "Expected to find input '{}' when aggregating to output '{}'".format(
                        input_name, output_name)
                input_spec = self.inputs[input_name]
                assert input_spec.shape == output_spec.shape, \
                    "Expected input {} and output {} spec shapes to match".format(
                        input_spec, output_spec)
                input_data = data_handle.get_data(input_name).as_ndarray()

                output_data += input_data

            data_handle.set_results(output_name, output_data)

    def _get_aggregate_map(self):
        return {
            'building_biomass_boiler': [
                'residential_biomass_boiler_biomass',
                'service_biomass_boiler_biomass',
            ],
            'building_elec_boiler': [
                'residential_electricity_boiler_electricity',
                'service_electricity_boiler_electricity',
            ],
            'building_heatpump': [
                'residential_electricity_heat_pumps_electricity',
                'service_electricity_heat_pumps_electricity',
            ],
            'building_gas_boiler': [
                'residential_gas_boiler_gas',
                'service_gas_boiler_gas',
            ],
            'building_hydrogen_boiler': [
                'residential_hydrogen_boiler_hydrogen',
                'service_hydrogen_boiler_hydrogen',
            ],
            'building_hydrogen_heatpump': [
                'residential_hydrogen_heat_pumps_hydrogen',
                'service_hydrogen_heat_pumps_hydrogen',
            ],
            'building_oil_boiler': [
                'residential_oil_boiler_oil',
                'service_oil_boiler_oil',
            ],
            'dh_biomass_boiler': [
                'residential_biomass_district_heating_biomass',
                'service_biomass_district_heating_biomass',
                'industry_biomass_district_heating_biomass',
            ],
            'dh_elec_boiler': [
                'residential_electricity_district_heating_electricity',
                'service_electricity_district_heating_electricity',
                'industry_electricity_district_heating_electricity',
            ],
            'dh_gas_CHP': [
                'residential_gas_district_heating_CHP_gas',
                'service_gas_district_heating_CHP_gas',
                'industry_gas_district_heating_CHP_gas',
            ],
            'dh_hydrogen_fuelcell': [
                'residential_hydrogen_district_heating_fuel_cell',
                'service_hydrogen_district_heating_fuel_cell',
                'residential_hydrogen_fuel_cell_hydrogen',
                'service_hydrogen_fuel_cell_hydrogen',
                'industry_hydrogen_district_heating_fuel_cell',
                'industry_hydrogen_fuel_cell_hydrogen',
            ],
            'elecload': [
                'industry_electricity_boiler_electricity',
                'industry_electricity_heat_pumps_electricity',
                'industry_electricity_non_heating',
            ],
            'gasload': [
                'industry_gas_non_heating',
                'industry_gas_boiler_gas',
            ],
            'hydrogen_non_heat_eh': [
                'residential_hydrogen_non_heating',
                'service_hydrogen_non_heating',
                'industry_hydrogen_boiler_hydrogen',
                'industry_hydrogen_heat_pumps_hydrogen',
                'industry_hydrogen_non_heating',
            ]
        }
