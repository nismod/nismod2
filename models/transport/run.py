"""Transport model wrapper
"""
# -*- coding: utf-8 -*-

import configparser
import csv
import os
from subprocess import check_output, CalledProcessError
from string import Template

import pandas as pd
import numpy as np
from smif.data_layer.data_array import DataArray
from smif.exception import SmifTimestepResolutionError
from smif.model.sector_model import SectorModel


class BaseTransportWrapper(SectorModel):
    """Base wrapper for the transport model - override private variables in implementations
    """
    def __init__(self, *args, **kwargs):
        # override these
        # self._config_filename
        # self._templates_dirname

        self._current_timestep = None
        self._set_options()
        super().__init__(*args, **kwargs)

    def _set_options(self):
        this_dir = os.path.dirname(__file__)

        config = configparser.ConfigParser()
        config.read(os.path.join(this_dir, self._config_filename))

        self._templates_dir = os.path.join(this_dir, 'templates', self._templates_dirname)

        if 'run' not in config:
            raise KeyError("Expected '[run]' section in transport run_config.ini")

        if 'jar' in config['run']:
            self._jar_path = os.path.join(this_dir, config['run']['jar'])
        else:
            raise KeyError("Expected 'jar' in transport run_config.ini")

        if 'working_dir' in config['run']:
            self._working_dir = os.path.join(this_dir, config['run']['working_dir'])
            self._input_dir = os.path.join(self._working_dir, 'input')
            self._output_dir = os.path.join(self._working_dir, 'output')
        else:
            raise KeyError("Expected 'data_dir' in transport run_config.ini")

        if 'optional_args' in config['run']:
            self._optional_args = config['run']['optional_args'].split(" ")
        else:
            self._optional_args = []

    def _output_file_path(self, filename):
        return os.path.join(self._output_dir, str(self._current_timestep), filename)

    def simulate(self, data):
        """Run the transport model

        Arguments
        ---------
        data: smif.data_layer.DataHandle
        """
        try:
            os.mkdir(self._input_dir)
        except FileExistsError:
            pass

        self._current_timestep = data.current_timestep
        self._set_parameters(data)
        self._set_inputs(data)
        self._set_properties(data)
        self._run_model_subprocess(data)
        self._set_outputs(data)

    def _run_model_subprocess(self, data_handle):
        """Run the transport model jar and feed log messages
        into the smif loggerlogger
        """

        working_dir = self._working_dir
        path_to_jar = self._jar_path

        path_to_config = os.path.join(working_dir, 'config', 'config.properties')

        self.logger.info("FROM run.py: Running transport model")
        arguments = ['java'] + self._optional_args + [
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
            self.logger.debug(arguments)
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
        input_dir = self._input_dir

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
        input_dir = self._input_dir

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
        colname = self.inputs['population'].dims[0]
        population = population.pivot(
            index='year', columns=colname, values='population'
        )
        population_filepath = os.path.join(
            input_dir, 'population.csv')
        population.to_csv(population_filepath)

        # GVA
        base_da = data_handle.get_base_timestep_data("gva")
        base_gva = base_da.as_df().reset_index()
        # work around smif not overriding source output name
        base_gva = base_gva.rename(columns={base_da.name: 'gva'})
        base_gva['year'] = data_handle.base_timestep

        current_da = data_handle.get_data("gva")
        current_gva = current_da.as_df().reset_index()
        # work around smif not overriding source output name
        current_gva = current_gva.rename(columns={current_da.name: 'gva'})
        current_gva['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            gva = pd.concat(
                [base_gva, current_gva]
            )
        else:
            gva = current_gva

        colname = self.inputs['gva'].dims[0]
        gva = gva.pivot(
            index='year', columns=colname, values='gva'
        )
        gva_filepath = os.path.join(input_dir, 'gva.csv')
        gva.to_csv(gva_filepath)

        # Fuel prices
        fuel_price = data_handle.get_data('fuel_price').as_df().reset_index()
        fuel_price['year'] = data_handle.current_timestep
        fuel_price = fuel_price.pivot(
            index='year', columns='transport_fuel_type', values='fuel_price'
        )
        fuel_price['ELECTRICITY'] = float(data_handle.get_data('fuel_price_electricity').data)

        fuel_price_filepath = os.path.join(input_dir, 'energyUnitCosts.csv')
        fuel_price.to_csv(fuel_price_filepath)

    def _set_properties(self, data_handle):
        """Set the transport model properties, such as paths and interventions
        """
        working_dir = self._working_dir
        path_to_config_templates = self._templates_dir

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
        # !!! hack: look through output dimensions to find LAD dimension name
        dims = self.outputs['electric_vehicle_trip_starts'].dims
        zone_dim = 'lad_uk_2016'  # sensible default for full model
        for dim in dims:
            if dim != 'annual_day_hours':
                # assume that time is 'annual_day_hours', so we want the other one
                zone_dim = dim

        # EV trip starts
        evt_name = 'electric_vehicle_trip_starts'
        ev_trips = self._melt_output(
            name=evt_name,
            filename=self._output_file_path('zonalTemporalEVTripStarts.csv'),
            dims={
                'zone': zone_dim,
                'hour': 'annual_day_hours'
            },
            csv_id_vars=['zone'],
            csv_melt_var='hour'
        )
        ev_trips = self._df_to_ndarray(evt_name, ev_trips)
        data_handle.set_results(evt_name, ev_trips)

        # EV consumption
        evc_name = 'electric_vehicle_electricity_consumption'
        ev_consumption = self._melt_output(
            name=evc_name,
            filename=self._output_file_path('zonalTemporalEVTripElectricity.csv'),
            dims={
                'zone': zone_dim,
                'hour': 'annual_day_hours'
            },
            csv_id_vars=['zone'],
            csv_melt_var='hour'
        )
        ev_consumption = self._df_to_ndarray(evc_name, ev_consumption)
        data_handle.set_results(evc_name, ev_consumption)

        # Energy consumption, all fuels
        ec_name = 'energy_consumption'
        energy_consumption = self._melt_output(
            name=ec_name,
            filename=self._output_file_path('energyConsumptions.csv'),
            dims={
                'fuel': 'transport_fuel_type'
            },
            csv_id_vars=[],
            csv_melt_var='fuel'
        )
        # Split - non-electricity (measured in litres)
        non_elec = energy_consumption.reset_index()
        non_elec = non_elec[non_elec.transport_fuel_type != 'ELECTRICITY']
        non_elec['annual_day'] = 'annual_day'
        non_elec = non_elec.set_index(['annual_day', 'transport_fuel_type'])
        print(non_elec)
        non_elec = self._df_to_ndarray(ec_name, non_elec)
        data_handle.set_results(ec_name, non_elec)
        # Split - electricity (measured in kWh)
        elec = np.array(energy_consumption.loc['ELECTRICITY'])
        data_handle.set_results('energy_consumption_electricity', elec)

    def _melt_output(self, name, filename, dims, csv_id_vars, csv_melt_var):
        return pd.read_csv(
            filename
        ).drop(
            'year', axis=1  # ignore the year output, assume it's always current timestep
        ).melt(
            id_vars=csv_id_vars,
            var_name=csv_melt_var,
            value_name=name
        ).rename(
            dims, axis=1
        ).set_index(
            sorted(dims.values())
        )

    def _df_to_ndarray(self, output_name, df):
        spec = self.outputs[output_name]
        da = DataArray.from_df(spec, df)
        return da.data


class TransportWrapper(BaseTransportWrapper):
    """Wrap the transport model, in 'full' configuration
    """
    def __init__(self, *args, **kwargs):
        # override these to configure 'full' model
        self._config_filename = 'run_config_full.ini'
        self._templates_dirname = 'full'
        super().__init__(*args, **kwargs)


class SouthamptonTransportWrapper(BaseTransportWrapper):
    """Wrap the transport model, in 'southampton' configuration
    """
    def __init__(self, *args, **kwargs):
        # override these to configure 'southampton' model
        self._config_filename = 'run_config_southampton.ini'
        self._templates_dirname = 'southampton'
        super().__init__(*args, **kwargs)
