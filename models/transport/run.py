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
    """Base wrapper for the transport model - override class variables in implementations
    """
    _config_filename = 'run_config.ini'
    _template_filename = 'config.properties.template'

    def __init__(self, *args, **kwargs):
        # shared setup
        self._current_timestep = None
        self._set_options()
        super().__init__(*args, **kwargs)

    def _set_options(self):
        this_dir = os.path.dirname(__file__)

        config = configparser.ConfigParser()
        config.read(os.path.join(this_dir, self._config_filename))

        self._templates_dir = os.path.join(this_dir, 'templates')

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
            self._config_path = os.path.join(self._working_dir, 'config.properties')
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

        self.logger.info("FROM run.py: Running transport model")
        base_arguments = ['java'] + self._optional_args + [
            '-cp',
            path_to_jar,
            'nismod.transport.App',
            '-c',
            self._config_path
        ]
        if data_handle.current_timestep == data_handle.base_timestep:
            base_arguments.append('-b')
            try:
                self.logger.debug(base_arguments)
                output = check_output(base_arguments)
                self.logger.info(output.decode("utf-8"))
            except CalledProcessError as ex:
                self.logger.error(ex.output.decode("utf-8"))
                self.logger.exception("Transport model failed %s", ex)
                raise ex
        else:
            tspt_model_arguments = base_arguments + [
                '-road',
                str(data_handle.current_timestep),
                str(data_handle.previous_timestep)
            ]
            try:
                self.logger.debug(tspt_model_arguments)
                output = check_output(tspt_model_arguments)
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
        self._set_population(data_handle)
        self._set_gva(data_handle)
        self._set_fuel_price(data_handle)
        self._set_engine_fractions(data_handle)

    def _set_population(self, data_handle):
        current_population = data_handle.get_data("population").as_df().reset_index()
        current_population['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            previous_population = data_handle.get_previous_timestep_data("population").as_df().reset_index()
            previous_population['year'] = data_handle.previous_timestep

            population = pd.concat(
                [previous_population, current_population]
            )
        else:
            population = current_population

        population.population = population.population.astype(int)
        # use region dimension name (could change) for columns
        colname = self.inputs['population'].dims[0]
        population = population.pivot(
            index='year', columns=colname, values='population'
        )
        population_filepath = os.path.join(
            self._input_dir, 'population.csv')
        population.to_csv(population_filepath)

    def _set_gva(self, data_handle):
        current_gva = data_handle.get_data("gva").as_df().reset_index()
        current_gva['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            previous_gva = data_handle.get_previous_timestep_data("gva").as_df().reset_index()
            previous_gva['year'] = data_handle.previous_timestep

            gva = pd.concat(
                [previous_gva, current_gva]
            )
        else:
            gva = current_gva

        # use region dimension name (could change) for columns
        colname = self.inputs['gva'].dims[0]
        gva = gva.pivot(
            index='year', columns=colname, values='gva'
        )
        gva_filepath = os.path.join(self._input_dir, 'gva.csv')
        gva.to_csv(gva_filepath)

    def _set_fuel_price(self, data_handle):
        fuel_price = data_handle.get_data('fuel_price').as_df().reset_index()
        fuel_price['year'] = data_handle.current_timestep
        fuel_price = fuel_price.pivot(
            index='year', columns='transport_fuel_type', values='fuel_price'
        )
        fuel_price['ELECTRICITY'] = float(data_handle.get_data('fuel_price_electricity').data)

        fuel_price_filepath = os.path.join(self._input_dir, 'energyUnitCosts.csv')
        fuel_price.to_csv(fuel_price_filepath)

    def _set_engine_fractions(self, data_handle):
        current_data = self._get_engine_fractions(data_handle, data_handle.current_timestep)

        if data_handle.current_timestep != data_handle.base_timestep:
            base_data = self._get_engine_fractions(data_handle, data_handle.base_timestep)

            data = pd.concat([base_data, current_data])
        else:
            data = current_data

        data.to_csv(
            os.path.join(self._input_dir, 'engineTypeFractions.csv'), index=False,
            float_format='%.15f')


    def _get_engine_fractions(self, data_handle, timestep):
        engine_fractions = data_handle.get_data(
            'engine_type_fractions', timestep=timestep).as_df().reset_index()
        engine_fractions = engine_fractions.pivot(
            index='vehicle_type', columns='engine_type', values='engine_type_fractions'
        )
        engine_fractions.columns = engine_fractions.columns.values
        engine_fractions = engine_fractions.reset_index().rename(
            columns={
                'vehicle_type': 'vehicle'
            }
        )
        engine_fractions['year'] = timestep

        # ensure column order matches EngineType enum definition (Java CSV reading assumes
        # fixed column order)
        column_order = [
            'year', 'vehicle', 'ICE_PETROL', 'ICE_DIESEL', 'ICE_LPG', 'ICE_H2', 'ICE_CNG',
            'HEV_PETROL', 'HEV_DIESEL', 'FCEV_H2', 'PHEV_PETROL', 'PHEV_DIESEL', 'BEV']
        engine_fractions = engine_fractions[column_order]
        return engine_fractions

    def _set_properties(self, data_handle):
        """Set the transport model properties, such as paths and interventions
        """
        working_dir = self._working_dir
        working_dir_path = str(os.path.abspath(working_dir)).replace('\\', '/')
        path_to_config_template = os.path.join(self._templates_dir, self._template_filename)

        # read config as a Template for easy substitution of values
        with open(path_to_config_template) as template_fh:
            config = Template(template_fh.read())

        intervention_files = []
        # Must be able to identify rail model interventions
        # the key in the config.properties must be railInterventionsFileX instead of
        # interventionsFilesX
        # Next line must contain all possible types of rail interventions
        rail_interventions_types = ['NewRailStation']
        for i, intervention in enumerate(data_handle.get_current_interventions().values()):
            fname = self._write_intervention(intervention)
            # write path with "/" separators even on Windows
            fname = fname.replace("\\", "/")
            if intervention['type'] in rail_interventions_types:
                intervention_files.append("railInterventionFile{} = {}".format(i, fname))
            else:
                intervention_files.append("interventionFile{} = {}".format(i, fname))

        config_str = config.substitute({
            'relative_path': working_dir_path,
            'intervention_files': '\n'.join(intervention_files),
            'link_travel_time_averaging_weight': \
                float(data_handle.get_parameter('link_travel_time_averaging_weight').data),
            'assignment_iterations': \
                int(data_handle.get_parameter('assignment_iterations').data),
            'prediction_iterations': \
                int(data_handle.get_parameter('prediction_iterations').data),
            'use_route_choice_model': \
                bool(data_handle.get_parameter('use_route_choice_model').data),
        })

        with open(self._config_path, 'w') as template_fh:
            template_fh.write(config_str)

    def _write_intervention(self, intervention):
        """Write a single intervention file, returning the full path
        """
        path = os.path.normpath(os.path.abspath(os.path.join(
            self._input_dir, "{}.properties".format(intervention['name']))))

        # compute start/end year from smif intervention keys
        intervention['startYear'] = intervention['build_year']
        intervention['endYear'] =  intervention['build_year'] + \
            intervention['technical_lifetime']['value']
        del intervention['build_year']
        del intervention['technical_lifetime']

        # fix up path to congestion charging pricing details file
        if 'congestionChargingPricing' in intervention:
            cccp_filename = intervention['congestionChargingPricing']
            intervention['congestionChargingPricing'] = os.path.join(
                self._working_dir, 'data', 'csvfiles', cccp_filename
            ).replace("\\", "/")

        print('Now writing {}'.format(path))
        with open(path, 'w') as file_handle:
            for key, value in intervention.items():
                file_handle.write("{} = {}\n".format(key, value))

        return path

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

        # EV trip starts and consumption
        evt_name = 'electric_vehicle_trip_starts'
        evc_name = 'electric_vehicle_electricity_consumption'

        # set up zero-valued output arrays
        ev_trips = np.zeros(self.outputs[evt_name].shape)
        ev_consumption = np.zeros(self.outputs[evc_name].shape)

        for vehicle_type in ('CAR', 'VAN', 'RIGID', 'ARTIC'):
            vehicle_ev_trips = self._melt_output(
                name=evt_name,
                filename=self._output_file_path(f'zonalTemporalEVTripStarts{vehicle_type}.csv'),
                dims={
                    'zone': zone_dim,
                    'hour': 'annual_day_hours'
                },
                csv_id_vars=['zone'],
                csv_melt_var='hour'
            )

            vehicle_ev_consumption = self._melt_output(
                name=evc_name,
                filename=self._output_file_path(f'zonalTemporalEVTripElectricity{vehicle_type}.csv'),
                dims={
                    'zone': zone_dim,
                    'hour': 'annual_day_hours'
                },
                csv_id_vars=['zone'],
                csv_melt_var='hour'
            )

            # sum up over vehicles (aggregated output)
            ev_trips += self._df_to_ndarray(evt_name, vehicle_ev_trips)
            ev_consumption += self._df_to_ndarray(evc_name, vehicle_ev_consumption)

        # Output EV trip starts and energy consumption
        data_handle.set_results(evt_name, ev_trips)
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
        non_elec = energy_consumption.copy()
        non_elec = non_elec[non_elec.transport_fuel_type != 'ELECTRICITY']
        non_elec['annual_day'] = 'annual_day'
        non_elec = self._df_to_ndarray(ec_name, non_elec)
        data_handle.set_results(ec_name, non_elec)
        # Split - electricity (measured in kWh)
        elec = energy_consumption[energy_consumption.transport_fuel_type == 'ELECTRICITY']
        elec = np.array(elec.energy_consumption)
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
        )

    def _df_to_ndarray(self, output_name, dataframe):
        spec = self.outputs[output_name]
        dataframe.set_index(spec.dims, inplace=True)
        dataarray = DataArray.from_df(spec, dataframe)
        return dataarray.data


class TransportWrapper(BaseTransportWrapper):
    """Wrap the transport model, in 'full' configuration
    """
    _config_filename = 'run_config_full.ini'
    _template_filename = 'gb-config.properties.template'


class SouthamptonTransportWrapper(BaseTransportWrapper):
    """Wrap the transport model, in 'southampton' configuration
    """
    _config_filename = 'run_config_southampton.ini'
    _template_filename = 'southampton-config.properties.template'
