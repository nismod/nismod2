"""Transport model wrapper
"""
# -*- coding: utf-8 -*-

import csv
import os
from subprocess import check_output, CalledProcessError
from string import Template

import pandas as pd
import numpy as np
from smif.exception import SmifTimestepResolutionError
from smif.model.sector_model import SectorModel


class TransportWrapper(SectorModel):
    """Wrap the transport model
    """
    def _get_working_dir(self):
        return os.path.join(
            os.path.dirname(__file__), '..', '..',
            'data', 'transport', 'TR_data_full_for_release_v2.0.0-alpha-5', 'full')

    def _get_input_dir(self):
        """Directory where this wrapper writes data/parameters
        """
        working_dir = self._get_working_dir()
        return os.path.join(working_dir, 'input')

    def _get_path_to_jar(self):
        return os.path.join(
            os.path.dirname(__file__), '..', '..',
            'install', 'transport', 'transport.jar')

    def _get_path_to_config_templates(self):
        return os.path.join(os.path.dirname(__file__), 'templates')

    def simulate(self, data):
        """Run the transport model

        Arguments
        ---------
        data: smif.data_layer.DataHandle
        """
        input_dir = self._get_input_dir()
        if not os.path.exists(input_dir):
            os.mkdir(input_dir)

        self._set_parameters(data)
        self._set_inputs(data)
        self._set_properties(data)
        self._run_model_subprocess(data)

        if data.current_timestep != data.base_timestep:
            self._set_outputs(data)
        else:
            msg = 'Transport model is using a workaround to produce outputs for the baseyear'
            self.logger.warning(msg)

            data.set_results(
                "energy_consumption", np.zeros((1, 5), dtype='float'))
            data.set_results(
                "energy_consumption_electricity", np.zeros((1,), dtype='float'))

    def _run_model_subprocess(self, data_handle):
        """Run the transport model jar and feed log messages
        into the smif loggerlogger
        """

        working_dir = self._get_working_dir()
        path_to_jar = self._get_path_to_jar()

        path_to_config = os.path.join(working_dir, 'config', 'config.properties')

        self.logger.info("FROM run.py: Running transport model")
        arguments = [
            'java',
            '-cp',
            path_to_jar,
            'nismod.transport.App',
            '-c',
            path_to_config
        ]
        if data_handle.current_timestep == data_handle.base_timestep:
            arguments.append('-b')
        else:
            arguments.extend([
                '-r',
                str(data_handle.current_timestep),
                str(data_handle.previous_timestep)
            ])

        try:
            output = check_output(arguments)
            self.logger.info(output.decode("utf-8"))
        except CalledProcessError as ex:
            self.logger.error(ex.output.decode("utf-8"))
            self.logger.exception("Transport model failed %s", ex)
            raise ex

    def _input_dimension_names(self, input_name, dimension_name):
        return self.inputs[input_name].dim_coords(dimension_name).ids

    def _set_parameters(self, data_handle):
        """Read model parameters from data handle and set up config files
        """
        input_dir = self._get_input_dir()

        # Elasticities for passenger and freight demand
        variables = ['POPULATION', 'GVA', 'TIME', 'COST']
        types = {
            'ETA': os.path.join(input_dir, 'elasticities.csv'),
            'FREIGHT_ETA': os.path.join(
                input_dir, 'elasticitiesFreight.csv')
        }
        for suffix, filename in types.items():
            with open(filename, 'w') as file_handle:
                writer = csv.writer(file_handle)
                writer.writerow(('variable', 'elasticity'))
                for variable in variables:
                    key = "{}_{}".format(variable, suffix)
                    value = float(data_handle.get_parameter(key).as_ndarray())
                    writer.writerow((variable, value))

    def _set_inputs(self, data_handle):
        """Get model inputs from data handle and write to input files
        """
        input_dir = self._get_input_dir()

        # Population
        base_population = data_handle.get_base_timestep_data("population").as_df().reset_index()
        base_population['year'] = data_handle.base_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            current_population = data_handle.get_data("population").as_df().reset_index()
            current_population['year'] = data_handle.current_timestep

            population = pd.concat(
                [base_population, current_population]
            )
        else:
            population = base_population

        population.population = population.population.astype(int)
        population = population.pivot(
            index='year', columns='lad_uk_2016', values='population'
        )
        population_filepath = os.path.join(
            input_dir, 'population.csv')
        population.to_csv(population_filepath)

        # GVA
        base_gva = data_handle.get_base_timestep_data("gva").as_df().reset_index()
        base_gva['year'] = data_handle.base_timestep

        current_gva = data_handle.get_data("gva").as_df().reset_index()
        current_gva['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            gva = pd.concat(
                [base_gva, current_gva]
            )
        else:
            gva = current_gva

        gva = gva.pivot(
            index='year', columns='lad_uk_2016', values='gva_per_head'
        )
        gva_filepath = os.path.join(input_dir, 'gva.csv')
        gva.to_csv(gva_filepath)

        # Fuel prices
        fuel_price = data_handle.get_data('fuel_price').as_df().reset_index()
        fuel_price['year'] = data_handle.current_timestep
        fuel_price = fuel_price.pivot(
            index='year', columns='transport_fuel_type', values='fuel_price'
        )
        print(fuel_price)
        fuel_price['ELECTRICITY'] = float(data_handle.get_data('fuel_price_electricity').data)
        print(fuel_price)

        fuel_price_filepath = os.path.join(input_dir, 'energyUnitCosts.csv')
        fuel_price.to_csv(fuel_price_filepath)

    def _set_properties(self, data_handle):
        """Set the transport model properties, such as paths and interventions
        """
        working_dir = self._get_working_dir()
        path_to_config_templates = self._get_path_to_config_templates()

        for root, _, filenames in os.walk(path_to_config_templates):
            for filename in filenames:
                with open(os.path.join(root, filename), 'r') as template_fh:
                    config = Template(template_fh.read())

                working_dir_path = str(os.path.abspath(working_dir)).replace('\\', '/')

                try:
                    prev = data_handle.previous_timestep
                except SmifTimestepResolutionError:
                    prev = None

                config_str = config.substitute({
                    'base_timestep': data_handle.base_timestep,
                    'previous_timestep': prev,
                    'current_timestep': data_handle.current_timestep,
                    'relative_path': working_dir_path
                })

                config_path = os.path.join(
                    working_dir,
                    os.path.relpath(root, path_to_config_templates),
                    filename.replace('.template', '')
                )
                with open(config_path, 'w') as template_fh:
                    template_fh.write(config_str)

    def _set_outputs(self, data_handle):
        """Read results from model and write to data handle
        """
        working_dir = self._get_working_dir()
        output_dir = os.path.join(working_dir, 'output', 'main')

        energy_consumption_file = os.path.join(
            output_dir, str(data_handle.current_timestep), 'energyConsumptions.csv')

        try:
            fuels = self.outputs['energy_consumption'].dim_coords('transport_fuel_type').ids
            consumption = {}
            with open(energy_consumption_file) as fh:
                r = csv.reader(fh)
                header = next(r)[1:]
                values = next(r)[1:]

                for fuel, val in zip(header, values):
                    consumption[fuel] = val

            data = np.zeros((1, len(fuels)))
            for i, fuel in enumerate(fuels):
                data[0, i] = consumption[fuel]

            data_handle.set_results(
                "energy_consumption",
                data
            )

            data_handle.set_results(
                "energy_consumption_electricity",
                np.array([float(consumption['ELECTRICITY'])])
            )

        except FileNotFoundError as ex:
            msg = "Cannot find the energy consumption file {}"
            raise FileNotFoundError(
                msg.format(energy_consumption_file)) from ex
