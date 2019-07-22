"""This adapter aggregates all inputs and writes the aggregate
values to each output
"""
import numpy as np
from smif.model import SectorModel


def _aggregate_inputs_to_output(data_handle, input_names, inputs, output_name, outputs):
    # check output exists
    assert output_name in outputs, \
        "Expected to find output '{}' when aggregating".format(output_name)

    # set up zero output
    output_spec = outputs[output_name]
    output_data = np.zeros(output_spec.shape)

    for input_name in input_names:
        # check input exists
        assert input_name in inputs, \
            "Expected to find input '{}' when aggregating to output '{}'".format(
                input_name, output_name)
        # check specs match
        input_spec = inputs[input_name]
        assert input_spec.shape == output_spec.shape, \
            "Expected input {} and output {} spec shapes to match".format(
                input_spec, output_spec)
        # add input to output data in-place
        input_data = data_handle.get_data(input_name).as_ndarray()
        output_data += input_data

    # write output
    data_handle.set_results(output_name, output_data)


class AggregateEnergyConstrained(SectorModel):
    """Aggregate inputs to outputs for energy models in constrained heat mode
    """
    def simulate(self, data_handle):
        to_output_from_inputs = self._get_aggregate_map()
        for output_name, input_names in to_output_from_inputs.items():
            _aggregate_inputs_to_output(
                data_handle, input_names, self.inputs, output_name, self.outputs)

    def _get_aggregate_map(self):
        return {
            'building_biomass_boiler': [
                'residential_biomass_boiler_biomass',
                'service_biomass_boiler_biomass',
                'industry_biomass_boiler_biomass',
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
                'industry_oil_boiler_oil',
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
            ],
            'oil_non_heat_eh': [
                'residential_oil_non_heating',
                'service_oil_non_heating',
                'industry_oil_non_heating',
            ],
            'building_solidfuel_boiler': [
                'residential_solid_fuel_boiler_solid_fuel',
                'service_solid_fuel_boiler_solid_fuel',
                'industry_solid_fuel_boiler_solid_fuel',
            ],
            'solid_fuel_non_heat_eh': [
                'residential_solid_fuel_non_heating',
                'service_solid_fuel_non_heating',
                'industry_solid_fuel_non_heating',
            ]
        }


class AggregateEnergyOptimised(SectorModel):
    """Aggregate inputs to outputs for energy models in unconstrained/optimised heat mode
    """
    def simulate(self, data_handle):
        to_output_from_inputs = self._get_aggregate_map()
        for output_name, input_names in to_output_from_inputs.items():
            _aggregate_inputs_to_output(
                data_handle, input_names, self.inputs, output_name, self.outputs)

    def _get_aggregate_map(self):
        return {
            'hydrogen_non_heat_eh': [
                'residential_hydrogen',
                'service_hydrogen',
                'industry_hydrogen'
            ],
            'heatload_com': [
                'service_heat',
                'industry_heat'
            ]
        }
