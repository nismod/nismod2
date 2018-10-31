# -*- coding: utf-8 -*-

import csv
import os

from subprocess import check_output, CalledProcessError
from string import Template
from tempfile import TemporaryDirectory

import pandas as pd
import numpy as np

from smif.model.sector_model import SectorModel

class TransportWrapper(SectorModel):
    """Wrap the transport model
    """
    def _get_working_dir(self):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'transport')

    def _get_path_to_jar(self):
        return os.path.join(os.path.dirname(__file__), '..', '..', 'install', 'transport',  'transport.jar')

    def _get_path_to_config_templates(self):
        return os.path.join(os.path.dirname(__file__), 'templates')

    def simulate(self, data_handle):
        """Run the transport model

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        """
        if data_handle.current_timestep != data_handle.base_timestep:
            self._set_parameters(data_handle)
            self._set_inputs(data_handle)
            self._set_properties(data_handle)
            self._run_model_subprocess(data_handle)
            self._set_outputs(data_handle)
        else:
            self.logger.warning('This model is using a workaround to produce outputs for the baseyear')

            data_handle.set_results("energy_consumption_diesel", np.array([[float(0)]]))
            data_handle.set_results("energy_consumption_electricity", np.array([[float(0)]]))
            data_handle.set_results("energy_consumption_hybrid", np.array([[float(0)]]))
            data_handle.set_results("energy_consumption_hydrogen", np.array([[float(0)]]))
            data_handle.set_results("energy_consumption_lpg", np.array([[float(0)]]))
            data_handle.set_results("energy_consumption_petrol", np.array([[float(0)]]))

    def _run_model_subprocess(self, data_handle):
        """Run the transport model jar and feed log messages
        into the smif logger
        """

        working_dir = self._get_working_dir()
        path_to_jar = self._get_path_to_jar()

        path_to_config = os.path.join(working_dir, 'config.properties')

        self.logger.info("FROM run.py: Running transport model")
        arguments = [
            'java',
            '-cp',
            path_to_jar,
            'nismod.transport.App',
            '-c',
            path_to_config
        ]

        try:
            output = check_output(arguments)
            self.logger.debug(output.decode("utf-8"))
        except CalledProcessError as ex:
            self.logger.exception("Transport model failed %s", ex)
            raise ex

    def _input_dimension_names(self, input_name, dimension_name):
        return self.inputs[input_name].dim_coords(dimension_name).ids

    def _set_parameters(self, data_handle):
        """Read model parameters from data handle and set up config files
        """
        working_dir = self._get_working_dir()
        # Elasticities for passenger and freight demand
        variables = ['POPULATION', 'GVA', 'TIME', 'COST']
        types = {
            'ETA': os.path.join(working_dir, 'csvfiles', 'elasticities.csv'),
            'FREIGHT_ETA': os.path.join(working_dir, 'csvfiles', 'elasticitiesFreight.csv')
        }
        for suffix, filename in types.items():
            with open(filename, 'w') as file_handle:
                writer = csv.writer(file_handle)
                writer.writerow(('variable','elasticity'))
                for variable in variables:
                    key = "{}_{}".format(variable, suffix)
                    value = data_handle.get_parameter(key)
                    writer.writerow((variable, value))

    def _set_inputs(self, data_handle):
        """Get model inputs from data handle and write to input files
        """
        working_dir = self._get_working_dir()

        if not os.path.exists(os.path.join(working_dir, 'data')):
            os.mkdir(os.path.join(working_dir, 'data'))

        population_filepath = os.path.join(working_dir, 'data', 'population.csv')

        base_population = data_handle.get_base_timestep_data("population").as_df()
        base_population = base_population.reset_index().rename(columns={
            0: 'population'
        })
        base_population['year'] = data_handle.base_timestep

        current_population = data_handle.get_data("population").as_df()
        current_population = current_population.reset_index().rename(columns={
            0: 'population'
        })
        current_population['year'] = data_handle.current_timestep

        population = pd.concat(
            [base_population, current_population]
        ).pivot(
            index='year', columns='lad_uk_2016', values='population'
        )

        population.to_csv(population_filepath)

        # set GVA
        gva_filepath = os.path.join(working_dir, 'data', 'gva.csv')

        base_gva = data_handle.get_base_timestep_data("gva").as_df()
        base_gva = base_gva.reset_index().rename(columns={
            0: 'gva'
        })
        base_gva['year'] = data_handle.base_timestep

        current_gva = data_handle.get_data("gva").as_df()
        current_gva = current_gva.reset_index().rename(columns={
            0: 'gva'
        })
        current_gva['year'] = data_handle.current_timestep

        gva = pd.concat(
            [base_gva, current_gva]
        ).pivot(
            index='year', columns='lad_uk_2016', values='gva'
        )
        gva.to_csv(gva_filepath)


    def _set_properties(self, data_handle):
        """Set the transport model properties, such as paths and interventions
        """
        working_dir = self._get_working_dir()
        path_to_config_templates = self._get_path_to_config_templates()

        for root, directories, filenames in os.walk(path_to_config_templates):
            for filename in filenames:
                with open(os.path.join(root,filename), 'r') as template_fh:
                    config = Template(template_fh.read())

                config_str = config.substitute({
                    'base_timestep': data_handle.base_timestep,
                    'current_timestep': data_handle.current_timestep,
                    'relative_path': os.path.abspath(working_dir)
                })

                with open(os.path.join(working_dir, os.path.relpath(root, path_to_config_templates),
                            filename.replace('.template', '')), 'w') as template_fh:
                    template_fh.write(config_str)

    def _set_outputs(self, data_handle):
        """Read results from model and write to data handle
        """
        working_dir = self._get_working_dir()

        energy_consumption_file = os.path.join(
            working_dir, 'output', str(data_handle.current_timestep), 'energyConsumptions.csv')

        try:
            with open(energy_consumption_file) as fh:
                r = csv.reader(fh)
                header = next(r)[1:]
                values = next(r)[1:]
                for fuel, val in zip(header, values):
                    data_handle.set_results(
                        "energy_consumption_{}".format(fuel.lower()),
                        np.array([[float(val)]])
                    )
        except FileNotFoundError as ex:
            raise FileNotFoundError("Cannot find the energy consumption file at %s",
                str(energy_consumption_file)) from ex
