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
        #        self._set_parameters(data)
        self._set_inputs(data)
        #        self._set_properties(data)
        #        self._run_model_subprocess(data)
        #        self._set_outputs(data)

    def _run_model_subprocess(self, data_handle):
        """Run the transport model jar and feed log messages
        into the smif loggerlogger
        """

        working_dir = self._working_dir
        path_to_jar = self._jar_path

        self.logger.info("FROM run.py: Running transport model")
        base_arguments = ['java'] + self._optional_args + [
            '-XX:MaxHeapSize=10g',
            '-cp',
            path_to_jar,
            'nismod.transport.App',
            '-c',
            self._config_path
        ]
        if data_handle.current_timestep == data_handle.base_timestep:
            pass
        else:
            tspt_model_arguments = base_arguments + [
                '-rail',
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
        
        # key = 'BaseYearYearUsage'
        # year_usage = data_handle.get_parameter(key).as_df().reset_index()
        # year_usage = year_usage.set_index(['NLC_southampton'])

        # key = 'BaseYearDayUsage'
        # day_usage = data_handle.get_parameter(key).as_df().reset_index()
        # day_usage = day_usage.set_index(['NLC_southampton'])
        
        # path = './data/interventions/transport_rail.csv'
        # df = pd.read_csv(path, index_col=0).loc[:,'Mode':]
        # result = pd.concat([year_usage, day_usage, df], axis=1, join_axes=[year_usage.index])
        # result.to_csv(os.path.join(input_dir,'baseYearRailUsageFastTrack.csv'))

        key = 'elasticities'
        elasticities = data_handle.get_parameter(key).as_df()
        elasticities.to_csv(os.path.join(input_dir,'elasticitiesRail.csv'))

    def _set_inputs(self, data_handle):
        """Get model inputs from data handle and write to input files
        """
        self._set_1D_input(data_handle, 'population', 'population.csv', dtype=int)
        self._set_1D_input(data_handle, 'gva', 'gva.csv')
        self._set_1D_input(data_handle, 'rail_journey_fares', 'railStationJourneyFares.csv')
        self._set_1D_input(data_handle, 'rail_journey_times',
                           'railStationGeneralisedJourneyTimes.csv')

        #self._set_population(data_handle)
#        self._set_gva(data_handle)
        #        self._set_journey_fares(data_handle)
        #        self._set_journey_times(data_handle)
        
    def _set_1D_input(self, data_handle, input_name, filename,dtype=None):
        """Get one dimensional model input from data handle and write to input file
        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        input_name
        filename: str
        dtype: type [optional]
        """

        current_input = data_handle.get_data(input_name).as_df().reset_index()
        current_input['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            previous_input = data_handle.get_data(input_name).as_df().reset_index()
            previous_input['year'] = data_handle.previous_timestep

            input_df = pd.concat(
                [previous_input, current_input]
            )
        else:
            input_df = current_input
        if dtype:
            input_df.loc[:,input_name] = input_df.loc[:,input_name].astype(dtype)
        colname = self.inputs[input_name].dims[0]
        input_df = input_df.pivot(
            index='year', columns=colname, values=input_name
        )
        input_filepath = os.path.join(
            self._input_dir, filename)
        input_df.to_csv(input_filepath)
            
    def _set_population(self, data_handle):
        current_population = data_handle.get_data("population").as_df().reset_index()
        current_population['year'] = data_handle.current_timestep

        if data_handle.current_timestep != data_handle.base_timestep:
            previous_population = data_handle.get_data("population").as_df().reset_index()
            previous_population['year'] = data_handle.previous_timestep

            population = pd.concat(
                [previous_population, current_population]
            )
        else:
            population = current_population

        #population.population = population.population.astype(int)
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

    def _set_journey_fares(self, data_handle):
        current_journey_fares = data_handle.get_data("rail_journey_fares").as_df().reset_index()
        current_journey_fares['year'] = data_handle.current_timestep
        if data_handle.current_timestep != data_handle.base_timestep:
            previous_journey_fares = \
            data_handle.get_previous_timestep_data("rail_journey_fares").as_df().reset_index()
            previous_journey_fares['year'] = data_handle.previous_timestep

            journey_fares = pd.concat(
                [previous_journey_fares, current_journey_fares]
            )
        else:
            journey_fares = current_journey_fares
        
        # use region dimension name (could change) for columns
        colname = self.inputs['rail_journey_fares'].dims[0]
        journey_fares = journey_fares.pivot(
            index='year', columns=colname, values='rail_journey_fares'
        )
        journey_fares_filepath = os.path.join(self._input_dir, 'railStationJourneyFares.csv')
        journey_fares.to_csv(journey_fares_filepath)
    
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
        rail_interventions_types = ['NewRailStation']
        if data_handle.current_timestep == data_handle.base_timestep:
            current_day_usage = data_handle.get_data("day_usage").as_df().reset_index()
            current_day_usage = current_day_usage.set_index(['stations_NLC'])
            current_year_usage = data_handle.get_data("year_usage").as_df().reset_index()
            current_year_usage = current_year_usage.set_index(['stations_NLC'])
            for i, intervention in enumerate(data_handle.get_current_interventions().values()):
                fname = self._write_intervention(intervention, current_day_usage,
                                                 current_year_usage)
                if intervention['type'] in rail_interventions_types:
                    intervention_files.append("railInterventionFile{} = {}".format(i, fname))
                else:
                    intervention_files.append("interventionFile{} = {}".format(i, fname))

        config_str = config.substitute({
            'relative_path': working_dir_path,
            'intervention_files': '\n'.join(intervention_files),
            'use_car_cost_from_road_model': \
                bool(data_handle.get_parameter('use_car_cost_from_road_model').data),
            'predict_intermediate_rail_years': \
                bool(data_handle.get_parameter('predict_intermediate_rail_years').data),
        })

        with open(self._config_path, 'w') as template_fh:
            template_fh.write(config_str)

    def _write_intervention(self, intervention, current_day_usage, current_year_usage):
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

        # add day and year usage
        intervention['dayUsage'] = current_day_usage.loc[intervention['NLC']].values[0]
        intervention['yearUsage'] = current_year_usage.loc[intervention['NLC']].values[0]

        # fix up path to congestion charging pricing details file
        if 'congestionChargingPricing' in intervention:
            cccp_filename = intervention['congestionChargingPricing']
            intervention['congestionChargingPricing'] = os.path.join(
                self._working_dir, 'data', 'csvfiles', cccp_filename
            )

        with open(path, 'w') as file_handle:
            for key, value in intervention.items():
                file_handle.write("{} = {}\n".format(key, value))

        return path

    def _set_outputs(self, data_handle):
        pass

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

class SouthamptonRailTransportWrapper(BaseTransportWrapper):
    """Wrap the rail model, in 'southampton' configuration
    """
    _config_filename = 'run_config_rail_southampton.ini'
    _template_filename = 'rail_southampton-config.properties.template'
