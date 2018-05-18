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

    def _get_path_to_config_template(self):
        return os.path.join(os.path.dirname(__file__), 'template.properties')

    def initialise(self, initial_conditions):
        """Set up model state using initial conditions (any data required for
        the base year which would otherwise be output by a previous timestep) as
        necessary.
        """
        pass

    def simulate(self, data_handle):
        """Run the transport model

        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        """
        if data_handle.current_timestep != data_handle.base_timestep:
            self._set_parameters(data_handle)
            self._set_inputs(data_handle)
            self._run_model_subprocess(data_handle)
            self._set_outputs(data_handle)

    def _run_model_subprocess(self, data_handle):
        path_to_jar = self._get_path_to_jar()

        path_to_config_template = self._get_path_to_config_template()

        working_dir = self._get_working_dir()

        path_to_config = os.path.join(working_dir, 'config.properties')

        with open(path_to_config_template, 'r') as template_fh:
            config = Template(template_fh.read())

        config_str = config.substitute({
            'base_timestep': data_handle.base_timestep,
            'current_timestep': data_handle.current_timestep,
            'relative_path': os.path.abspath(working_dir)
        })

        with open(path_to_config, 'w') as template_fh:
            template_fh.write(config_str)

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

    def _input_region_names(self, input_name):
        return self.inputs[input_name].spatial_resolution.get_entry_names()

    def _input_interval_names(self, input_name):
        return self.inputs[input_name].temporal_resolution.get_entry_names()

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
        # TODO with OA-level data
        # areaCodeFileName = nomisPopulation.csv
        # area_code,zone_code,population
        # OA        LAD       integer count of people

        # populationFile = population.csv
        # year,          E06000045,E07000086,E07000091,E06000046
        # base/current   [LAD,...]
        # 2015,          247000,129000,179000,139000
        # 2020,          247000,129000,179000,139000
        if not os.path.exists(os.path.join(working_dir, 'data')):
            os.mkdir(os.path.join(working_dir, 'data'))

        with open(os.path.join(working_dir, 'data', 'population.csv') ,'w') as file_handle:
            w = csv.writer(file_handle)

            pop_region_names = self._input_region_names("population")
            w.writerow(('year', ) + tuple(pop_region_names))

            base_population = [int(population) for population in data_handle.get_base_timestep_data("population")[:,0]]
            w.writerow((data_handle.base_timestep, ) + tuple(base_population))

            current_population = [int(population) for population in data_handle.get_data("population")[:,0]]
            w.writerow((data_handle.current_timestep, ) + tuple(current_population))

        with open(os.path.join(working_dir, 'data', 'gva.csv') ,'w') as file_handle:
            w = csv.writer(file_handle)

            gva_region_names = self._input_region_names("gva")
            w.writerow(('year', ) + tuple(gva_region_names))

            base_gva = data_handle.get_base_timestep_data("gva")[:,0]
            w.writerow((data_handle.base_timestep, ) + tuple(base_gva))

            current_gva = data_handle.get_data("gva")[:,0]
            w.writerow((data_handle.current_timestep, ) + tuple(current_gva))

        # TODO base and current gva_per_head
        # GVAFile = GVA.csv
        # year,          E06000045,E07000086,E07000091,E06000046
        # base/current   [LAD,...]
        # 2015,          23535.00,27860.00,24418.00,17739.00
        # 2020,          23535.00,27860.00,24418.00,17739.00

    def _set_outputs(self, data_handle):
        """Read results from model and write to data handle
        """
        working_dir = self._get_working_dir()
        # energyConsumptions.csv
        # year,PETROL,DIESEL,LPG,ELECTRICITY,HYDROGEN,HYBRID
        # 2020,11632.72,17596.62,2665.98,7435.64,94.57,714.32

        energy_consumption_file = os.path.join(working_dir, 'output', 'energyConsumptions.csv')

        if not os.path.exists(energy_consumption_file):
            raise FileNotFoundError("Cannot find the energy consumption file at %s",
                str(energy_consumption_file))
        else:
            with open(os.path.join(working_dir, 'output', 'energyConsumptions.csv')) as fh:
                r = csv.reader(fh)
                header = next(r)[1:]
                values = next(r)[1:]
                for fuel, val in zip(header, values):
                    data_handle.set_results(
                        "energy_consumption__{}".format(fuel.lower()),
                        np.array([[float(val)]])
                    )

    def extract_obj(self, results):
        """Return value of objective function, to-be-defined
        """
        pass
