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
        if self._current_timestep > data.base_timestep:
            self._set_parameters(data)
            self._set_inputs(data)
            self._set_properties(data)
            self._run_model_subprocess(data)
            self._set_outputs(data)
        else:
            self._set_base_demand_output(data)

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
        # Set elasticities for rail model
        elasticities = data_handle.get_parameter('elasticities').as_df()
        elasticities.to_csv(os.path.join(self._input_dir,'elasticitiesRail.csv'))

    def _set_inputs(self, data_handle):
        """Get model inputs from data handle and write to input files
        """
        self._set_1D_input(data_handle, 'population', 'population.csv', dtype=int)
        self._set_1D_input(data_handle, 'gva', 'gva.csv')
        self._set_1D_input(data_handle, 'rail_journey_fares', 'railStationJourneyFares.csv')
        self._set_1D_input(data_handle, 'rail_journey_times',
                           'railStationGeneralisedJourneyTimes.csv')
        self._set_1D_input(data_handle, 'car_zonal_journey_costs', 'carZonalJourneyCosts.csv')
        self._set_trip_rates(data_handle)
        self._set_base_year_demand(data_handle)

    def _set_1D_input(self, data_handle, input_name, filename,dtype=None):
        """Get one dimensional model input from data handle and write to input file
        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        input_name: str
        filename: str
        dtype: type [optional]
        """

        current_input = data_handle.get_data(input_name).as_df().reset_index()
        current_input['year'] = data_handle.current_timestep
        #   lad_southampton     population  year
        # 0       E06000045  245280.036690  2015
        # 1       E07000086  140288.654932  2015
        # 2       E07000091  130489.400749  2015
        # 3       E06000046  180185.495562  2015

        previous_input = data_handle.get_previous_timestep_data(input_name).as_df().reset_index()
        previous_input['year'] = data_handle.previous_timestep

        input_df = pd.concat(
            [previous_input, current_input]
        )

        if dtype:
            input_df.loc[:,input_name] = input_df.loc[:,input_name].astype(dtype)

        # Now reshaping the dataframe for the corresponding CSV file to be readable
        # by the rail model.
        # For example

        #       lad_southampton  population  year
        # 0       E06000045      245280  2015
        # 1       E07000086      140288  2015
        # 2       E07000091      130489  2015
        # 3       E06000046      180185  2015
        # 0       E06000045      252308  2020
        # 1       E07000086      142705  2020
        # 2       E07000091      136404  2020
        # 3       E06000046      185906  2020

        # to

        #       lad_southampton  E06000045  E06000046  E07000086  E07000091
        # year
        # 2015                245280     180185     140288     130489
        # 2020                252308     185906     142705     136404

        colname = self.inputs[input_name].dims[0]
        input_df = input_df.pivot(
            index='year', columns=colname, values=input_name
        )
        # Write CSV input file for rail model
        input_filepath = os.path.join(
            self._input_dir, filename)
        input_df.to_csv(input_filepath)

    def _set_trip_rates(self, data):
        """Get trip rates input from data handle and write to input file
        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        """
        input_name = 'rail_trip_rates'
        filename = 'railTripRates.csv'
        # Get trip rate for current year
        input_df = data.get_data(input_name).as_df()
        input_df['year'] = data.current_timestep
        input_df = input_df.set_index(['year'])

        # The rail model requires data from base year to current year
        # Loop from year before current year to base year and concat dataframes
        for timestep in range(data.base_timestep,data.current_timestep)[::-1]:
            previous_input = data.get_data(input_name, timestep=timestep).as_df()
            previous_input['year'] = timestep
            previous_input = previous_input.set_index(['year'])
            input_df = pd.concat(
                [previous_input, input_df]
            )

        input_filepath = os.path.join(
            self._input_dir, filename)
        input_df.to_csv(input_filepath)

    def _set_base_year_demand(self, data_handle):
        """Write base year rail demand based on initial conditions.
        Arguments:
        ----------
        data_handle: smif.data_layer.DataHandle
        """
        # filter interventions to only get initial conditions
        # (build_year < base_year)
        interventions = self._filter_interventions(data_handle, future=False)
        # build dataframe and drop data that does not go into the
        # base year rail demand input file
        df = pd.DataFrame.from_dict(interventions)
        df = df.rename(columns={'NLC': 'NLC_gb'}).set_index('NLC_gb')
        df.index.names = ['NLC']
        cols_to_drop = ['technical_lifetime_units',
                        'technical_lifetime', 'name', 'type', 'build_year']
        df = df.drop(cols_to_drop, axis=1)
        # Get day and year usage from data_handle
        # (provided by station_usage scenario)
        NLC_dim = self.inputs['day_usage'].dims[0] # Name of NLC dimension in smif
        baseyear_day_usage = data_handle.get_data("day_usage",
                                                  timestep=data_handle.base_timestep)
        baseyear_day_usage = baseyear_day_usage.as_df().reset_index()
        baseyear_day_usage = baseyear_day_usage.set_index([NLC_dim])
        baseyear_day_usage.index.names = ['NLC']

        baseyear_year_usage = data_handle.get_data("year_usage",
                                                   timestep=data_handle.base_timestep)
        baseyear_year_usage = baseyear_year_usage.as_df().reset_index()
        baseyear_year_usage = baseyear_year_usage.set_index([NLC_dim])
        baseyear_year_usage.index.names = ['NLC']

        # current_day_usage also contains potential future rail stations
        # so must concat dataframes according to index of df that only contains old
        # stations
        df = pd.concat([df, baseyear_day_usage, baseyear_year_usage], axis=1,
                       join_axes=[df.index])
        # Hack year usage column in baseYearRailDemand.csv should contain integers
        df.year_usage = df.year_usage.astype(int)
        print(df)
        # rename columns to meet rail model's expectations
        columns_names = {
            'mode': 'Mode',
            'station': 'Station',
            'naPTANname': 'NaPTANname',
            'easting': 'Easting',
            'northing': 'Northing',
            'year_usage': 'YearUsage',
            'day_usage': 'DayUsage',
            'runDays': 'RunDays',
            'LADcode': 'LADcode',
            'LADname': 'LADname',
            'area': 'Area',
        }
        cols = ['Mode', 'Station', 'NaPTANname', 'Easting', 'Northing',
                'YearUsage', 'DayUsage', 'RunDays', 'LADcode', 'LADname', 'Area']
        df = df.rename(columns=columns_names)[cols]

        # Write base year rail demand csv file
        df.to_csv(os.path.join(self._input_dir, 'baseYearRailDemand.csv'))

            
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
        # Discard initial conditions if current year is the base year
        interventions = self._filter_interventions(data_handle)
        for i, intervention in enumerate(interventions):
            fname = self._write_rail_intervention(intervention, data_handle)
            intervention_files.append("railInterventionFile{} = {}".format(i, fname))

        config_str = config.substitute({
            'relative_path': working_dir_path,
            'intervention_files': '\n'.join(intervention_files),
            'use_car_cost_from_road_model': \
                bool(data_handle.get_parameter('use_car_cost_from_road_model').data),
            'predict_intermediate_rail_years': \
                bool(data_handle.get_parameter('predict_intermediate_rail_years').data),
            'base_year': \
                int(data_handle.get_parameter('base_year').data),
        })

        with open(self._config_path, 'w') as template_fh:
            template_fh.write(config_str)

    def _filter_interventions(self, data_handle, future=True):
        """Returns a list of interventions, containing *only* interventions
        occuring {strictly before} or after the base year.
        Default is to keep interventions occuring after the base year.
        (In other words, it filters out initial conditions)
        Arguments:
        ---------
        data_handle: smif.data_layer.DataHandle
        future: bool - If True, then select past interventions (initial conditions)
        Returns:
        --------
        interventions: list[dict]
        """
        interventions = []
        for i, intervention in enumerate(data_handle.get_current_interventions().values()):
            if(future):
                if intervention['build_year'] >= data_handle.base_timestep:
                    interventions.append(intervention)
            else:
                    if intervention['build_year'] < data_handle.base_timestep:
                        interventions.append(intervention)
        return interventions
    
    def _write_rail_intervention(self, intervention, data_handle):
        """Write a single intervention file, returning the full path
        """
        path = os.path.normpath(os.path.abspath(os.path.join(
            self._input_dir, "{}.properties".format(intervention['name']))))

        # add day and year usage
        build_year=intervention['build_year']
        NLC_dim = self.inputs['day_usage'].dims[0] # Name of NLC dimension in smif
        # day usage
        day_usage = data_handle.get_data("day_usage", timestep=build_year).as_df().reset_index()
        day_usage = day_usage.set_index([NLC_dim])
        intervention['dayUsage'] = day_usage.loc[intervention['NLC']].values[0]
        # year usage
        year_usage = data_handle.get_data("year_usage", timestep=build_year).as_df().reset_index()
        year_usage = year_usage.set_index([NLC_dim])
        intervention['yearUsage'] = int(year_usage.loc[intervention['NLC']].values[0])

        # compute start/end year from smif intervention keys
        intervention['startYear'] = intervention['build_year']
        intervention['endYear'] =  intervention['build_year'] + \
            intervention['technical_lifetime']['value']
        del intervention['build_year']
        del intervention['technical_lifetime']

        with open(path, 'w') as file_handle:
            for key, value in intervention.items():
                file_handle.write("{} = {}\n".format(key, value))

        return path

    def _set_outputs(self, data_handle):
        # Name of NLC dimension in smif
        NLC_dim = self.inputs['day_usage'].dims[0]
        # Name of LAD dimension in smif
        lad_dim = self.inputs['population'].dims[0]

        cols = {
            'NLC': NLC_dim,
            'YearUsage': 'year_stations_usage'
        }
        self._set_1D_output(data_handle, 'year_stations_usage',
                            self._output_file_path('predictedRailDemand.csv'), cols)
        cols = {
            'NLC': NLC_dim,
            'DayUsage': 'day_stations_usage'
        }
        self._set_1D_output(data_handle, 'day_stations_usage',
                            self._output_file_path('predictedRailDemand.csv'), cols)
        cols = {
            'LADcode': lad_dim,
            'yearTotal': 'total_year_zonal_rail_demand'
        }
        self._set_1D_output(data_handle, 'total_year_zonal_rail_demand',
                            self._output_file_path('zonalRailDemand.csv'), cols)
        cols = {
            'LADcode': lad_dim,
            'yearAvg': 'avg_year_zonal_rail_demand'
        }
        self._set_1D_output(data_handle, 'avg_year_zonal_rail_demand',
                            self._output_file_path('zonalRailDemand.csv'), cols)
        cols = {
            'LADcode': lad_dim,
            'dayTotal': 'total_day_zonal_rail_demand'
        }
        self._set_1D_output(data_handle, 'total_day_zonal_rail_demand',
                            self._output_file_path('zonalRailDemand.csv'), cols)
        cols = {
            'LADcode': lad_dim,
            'dayAvg': 'avg_day_zonal_rail_demand'
        }
        self._set_1D_output(data_handle, 'avg_day_zonal_rail_demand',
                            self._output_file_path('zonalRailDemand.csv'), cols)

    def _set_base_demand_output(self, data_handle):
        # Name of NLC dimension in smif
        NLC_dim = self.inputs['day_usage'].dims[0]
        # Name of LAD dimension in smif
        lad_dim = self.inputs['population'].dims[0]

        base_year_demand_file = os.path.join(self._input_dir,
                                             'baseYearRailDemand.csv')
        cols = {
            'NLC': NLC_dim,
            'YearUsage': 'year_stations_usage'
        }
        self._set_1D_output(data_handle, 'year_stations_usage',
                            base_year_demand_file, cols)
        cols = {
            'NLC': NLC_dim,
            'DayUsage': 'day_stations_usage'
        }
        self._set_1D_output(data_handle, 'day_stations_usage',
                         base_year_demand_file, cols)
        
    def _set_1D_output(self, data_handle, output_name, filename, cols):
        """Get one dimensional model input from data handle and write to input file
        Arguments
        ---------
        data_handle: smif.data_layer.DataHandle
        output_name
        filename: str
        cols: dict - Labels of the columns to keep. 
                     Keys are label in the ouput file.
                     Values are label in data_handle.
        """
        df = pd.read_csv(filename)
        df = df.loc[:,cols.keys()].rename(columns=cols)
        numpy_array = self._df_to_ndarray(output_name, df)
        data_handle.set_results(output_name, numpy_array)
        
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

class RailTransportWrapper(BaseTransportWrapper):
    """Wrap the rail model, in 'southampton' configuration
    """
    _config_filename = 'run_config_full.ini'
    _template_filename = 'rail-config.properties.template'
