"""The sector model wrapper for smif to run the energy demand model
"""
import os
import logging
import configparser
import numpy as np
from datetime import date
from collections import defaultdict
from smif.model.sector_model import SectorModel
from pkg_resources import Requirement, resource_filename
import math
from energy_demand.read_write import read_data

REGION_SET_NAME = 'lad_gb_2016'

import os
import sys
import csv
import logging
import numpy as np
import pandas as pd


class ETWrapper(SectorModel):
    """Energy Demand Wrapper
    """
    def __init__(self, name):
        super().__init__(name)
        self.user_data = {}

    def array_to_dict(self, input_array):
        """Convert array to dict

        Arguments
        ---------
        input_array : numpy.ndarray
            timesteps, regions, interval

        Returns
        -------
        output_dict : dict
            timesteps, region, interval

        """
        output_dict = defaultdict(dict)
        for r_idx, region in enumerate(self.get_region_names(REGION_SET_NAME)):
            output_dict[region] = input_array[r_idx, 0]

        return dict(output_dict)

    def before_model_run(self, data_handle=None):
        """Implement this method to conduct pre-model run tasks

        Arguments
        ---------
        data_handle : smif.data_layer.DataHandle
            Access parameter values (before any model is run, no dependency
            input data or state is guaranteed to be available)

        Info
        -----
        `self.user_data` allows to pass data from before_model_run to main model
        """
        pass

    def initialise(self, initial_conditions):
        """
        """
        pass

    def simulate(self, data_handle):
        """Runs the Energy Demand model for one `timestep`

        Arguments
        ---------
        data_handle : smif.data_layer.DataHandle

        Returns
        =======
        et_module_out : dict
            Outputs of et_module
        """
        logging.info("... start et_module")

        # ------------------------
        # Capacity based appraoch
        # ------------------------

        # ------------------------
        # Load data
        # ------------------------
        main_path = os.path.dirname(os.path.abspath(__file__))
        path_input_data = os.path.join(main_path, 'data', 'scenarios')

        regions = self.inputs['ev_trips'].dim_coords(REGION_SET_NAME).ids

        nr_of_regions = len(regions)

        simulation_yr = data_handle.current_timestep

        # Read number of EV trips starting in regions (np.array(regions, 24h))
        reg_trips_ev_24h = data_handle.get_data('ev_trips').as_ndarray()

        # Get hourly demand data for day for every region (np.array(regions, 24h)) (kWh)
        reg_elec_24h = data_handle.get_data('ev_electricity').as_ndarray()

        # --------------------------------------
        # Assumptions
        # --------------------------------------
        assumption_nr_ev_per_trip = 1               # [-] Number of EVs per trip
        assumption_ev_p_with_v2g_capability = 1.0   # [%] Percentage of EVs not used for v2g and G2V
        assumption_av_charging_state = 0.5          # [%] Assumed average charging state of EVs before peak trip hour
        assumption_av_usable_battery_capacity = 30  # [kwh] Average (storage) capacity of EV Source: https://en.wikipedia.org/wiki/Electric_vehicle_battery
        assumption_safety_margin = 0.1              # [%] Assumed safety margin (minimum capacity SOC)

        # --------------------------------------
        # 1. Find peak demand hour for EVs
        # --------------------------------------
        # Hour of electricity peak demand in day
        reg_peak_position_h_elec = np.argmax(reg_elec_24h, axis=1)

        # Total electricity demand of all trips of all vehicles
        reg_peak_demand_h_elec = np.max(reg_elec_24h, axis=1)

        # --------------------------------------
        # 2. Get number of EVs in peak hour with
        # help of trip number
        # --------------------------------------
        reg_max_nr_ev = np.zeros((nr_of_regions))
        for region_nr, peak_hour_nr in enumerate(reg_peak_position_h_elec):
            reg_max_nr_ev[region_nr] = reg_trips_ev_24h[region_nr][peak_hour_nr] * assumption_nr_ev_per_trip

        # --------------------------------------
        # 3. Calculate total EV battery capacity
        # of all vehicles which can do V2G
        # --------------------------------------

        # Number of EVs with V2G capability
        reg_nr_v2g_ev = reg_max_nr_ev * assumption_ev_p_with_v2g_capability

        # Demand in peak hour of all EVs with V2G capabilityies
        average_demand_vehicle = reg_peak_demand_h_elec / reg_max_nr_ev
        average_demand_vehicle[np.isnan(average_demand_vehicle)] = 0 #replace nan with 0
        average_demand_vehicle[np.isinf(average_demand_vehicle)] = 0 #replace inf with 0

        # Calculate peak demand of all vehicles with V2G capability
        reg_peak_demand_h_elec_v2g_ev = average_demand_vehicle * reg_nr_v2g_ev

        # Calculate overall maximum capacity of all EVs with V2G capabilities
        reg_max_capacity_v2g_ev = reg_nr_v2g_ev * assumption_av_usable_battery_capacity

        # --------------------------------------
        # 4. Calculate flexible "EV battery" used for G2V and v2g
        # -------------------------------------
        # Calculated capacity of safety margin (blue area)
        capacity_safety_margin = reg_max_capacity_v2g_ev * assumption_safety_margin

        # Calculate maximum possible V2G capacity
        actual_v2g_capacity = np.zeros((nr_of_regions))

        # Itereage regions and check whether the actual
        # consumption including safety margin is larger
        # than the demand based on the average soc assumption
        for region_nr, reg_peak_h_capacity in enumerate(reg_max_capacity_v2g_ev):

            # Actual used capacity of all vehicles with V2G capabilities and minimum charging state
            used_capacity_incl_margin = reg_peak_demand_h_elec_v2g_ev[region_nr] + capacity_safety_margin[region_nr]

            # Cannot be higher than maximum storage capacity
            if (used_capacity_incl_margin > reg_peak_demand_h_elec_v2g_ev[region_nr]):
                used_capacity = reg_peak_demand_h_elec_v2g_ev[region_nr]
            else:
                pass

            # Capacity necessary for assumed average SOC of region
            average_soc_capacity = assumption_av_charging_state * reg_peak_h_capacity

            # If average state of charging smaller than actual used capacity
            # the V2G capacity gets reduced
            if used_capacity > average_soc_capacity:

                # More is use than minimum SOC
                actual_v2g_capacity[region_nr] = reg_peak_h_capacity - used_capacity

                if (reg_peak_h_capacity - used_capacity) < 0:
                    actual_v2g_capacity[region_nr] = 0

                # Test that not minus capacity
                #assert (reg_peak_h_capacity - used_capacity) >= 0
            else:
                # Less is use than minimum SOC
                actual_v2g_capacity[region_nr] = reg_peak_h_capacity - average_soc_capacity

                if (reg_peak_h_capacity - average_soc_capacity) < 0:
                    actual_v2g_capacity[region_nr] = 0

                # Test that not minus capacity
                #assert (reg_peak_h_capacity - average_soc_capacity) >= 0

        data_handle.set_results('v2g_g2v_capacity', actual_v2g_capacity)

        '''# ---------------------
        # Load input variables
        # ---------------------

        # Define base year
        base_yr = 2015

        # Scenario parameters from narrative YAML file
        yr_until_changed = data_handle.get_parameter('yr_until_changed_lp')                 # Year until regime would be fully realised
        load_profile_scenario = data_handle.get_parameter('load_profile_charging_regime')   # Sheduled or unsheduled

        # Regions
        logging.info("... loading regions")
        regions = self.get_region_names(REGION_SET_NAME)

        # Current year of simulation
        logging.info("... loading base and simulation year")
        simulation_yr = data_handle.current_timestep

        # Hourly transport demand of simulation year (electrictiy)
        logging.info("... loading transport input")
        elec_array_data = data_handle.get_base_timestep_data('electricity')
        et_demand_elec_input = self.array_to_dict(elec_array_data)

        # Paths where csv profile are stored
        logging.info("... loading paths")
        main_path = os.path.dirname(os.path.abspath(__file__))
        csv_path_lp = os.path.join(main_path, '_config_data')

        # ------------------------------------
        # Load EV charging load profiles
        # ------------------------------------
        load_profiles = main_functions.get_load_profiles(
            csv_path_lp)
        logging.info("... load load profiles")

        # ------------------
        # Temporal disaggregation of load profile
        # ------------------
        logging.info("changing load profile")
        reg_et_demand_yh = main_functions.load_curve_assignement(
            curr_yr=simulation_yr,
            base_yr=base_yr,
            yr_until_changed=yr_until_changed,
            et_service_demand_yh=et_demand_elec_input,
            load_profiles=load_profiles,
            regions=regions,
            charging_scenario=load_profile_scenario,
            diffusion='sigmoid')

        et_module_out = {}
        et_module_out['electricity'] = reg_et_demand_yh

        # -------
        # Testing
        # -------
        assert round(np.sum(et_module_out['electricity']), 2) == round(sum(et_demand_elec_input.values()), 2)

        print("... Finished running et_module")
        return et_module_out'''

    def extract_obj(self, results):
        return 0

"""Diffusion functions
"""

def linear_diff(base_yr, curr_yr, value_start, value_end, yr_until_changed):
    """Calculate a linear diffusion for a current year. If
    the current year is identical to the base year, the
    start value is returned

    Arguments
    ----------
    base_yr : int
        The year of the current simulation
    curr_yr : int
        The year of the current simulation
    value_start : float
        Fraction of population served with fuel_enduse_switch in base year
    value_end : float
        Fraction of population served with fuel_enduse_switch in end year
    yr_until_changed : str
        Year until changed is fully implemented

    Returns
    -------
    fract_cy : float
        The fraction in the simulation year
    """
    # Total number of simulated years
    sim_years = yr_until_changed - base_yr  + 1

    if curr_yr == base_yr or sim_years == 0 or value_end == value_start:
        fract_cy = value_start
    else:
        #-1 because in base year no change
        fract_cy = ((value_end - value_start) / (sim_years - 1)) * (curr_yr - base_yr) + value_start

    return fract_cy

def sigmoid_diffusion(base_yr, curr_yr, end_yr, sig_midpoint, sig_steeppness):
    """Calculates a sigmoid diffusion path of a lower to a higher value with
    assumed saturation at the end year

    Arguments
    ----------
    base_yr : int
        Base year of simulation period
    curr_yr : int
        The year of the current simulation
    end_yr : int
        The year a fuel_enduse_switch saturaes
    sig_midpoint : float
        Mid point of sigmoid diffusion function can be used to shift
        curve to the left or right (standard value: 0)
    sig_steeppness : float
        Steepness of sigmoid diffusion function The steepness of the
        sigmoid curve (standard value: 1)

    Returns
    -------
    cy_p : float
        The fraction of the diffusion in the current year

    Note
    ----
    It is always assuemed that for the simulation year the share is
    replaced with technologies having the efficencies of the current year.
    For technologies which get replaced fast (e.g. lightbulb) this
    is corret assumption, for longer lasting technologies, this is
    more problematic (in this case, over every year would need to be iterated
    and calculate share replaced with efficiency of technology in each year).

    Always returns positive value. Needs to be considered for changes in negative
    """
    if curr_yr == base_yr:
        return 0
    elif curr_yr == end_yr:
        return 1
    else:
        # Translates simulation year on the sigmoid graph reaching from -6 to +6 (x-value)
        if end_yr == base_yr:
            y_trans = 5.0
        else:
            y_trans = -5.0 + (10.0 / (end_yr - base_yr)) * (curr_yr - base_yr)

        # Get a value between 0 and 1 (sigmoid curve ranging from 0 to 1)
        cy_p = 1.0 / (1 + math.exp(-1 * sig_steeppness * (y_trans - sig_midpoint)))

        return cy_p

def load_curve_assignement(
        curr_yr,
        base_yr,
        yr_until_changed,
        et_service_demand_yh,
        load_profiles,
        regions,
        charging_scenario,
        diffusion='linear'
    ):
    """Assign input electrictiy demand (given as "tranport service"
    for every hour in a year) to an hourly energy demand load profile
    depending (see documentation for more information).

    Arguments
    =========
    curr_yr : int
        Current simulation year
    base_yr : int
        Base year of simulation
    yr_until_changed : int
        Year until changed is fully implemented
    et_service_demand_yh : dict
        Transport energy demand for every region (hourly demand)
    load_profiles : list
        Load profile objects
    regions : list
        All region names
    charging_scenario : str
        Scenario

            'sheduled' :

            'sheduled' : 
            TODO

    diffusion : str
        Type of diffusion between base year and end year load profile

            'linear':   Linear change over time towards future load profile

            'sigmoid':  Sigmoid change over time towards future load profile

    Returns
    =========
    et_demand_yh : array
        Houlry demand, np.array(reg_array_nr, 8760 timesteps)
    """
    et_demand_yh = np.zeros((len(regions), 365 * 24), dtype=float)

    # -------------------
    # Calculate diffusion
    # -------------------
    if diffusion == 'linear':
        simulation_year_p = diffusion_functions.linear_diff(
            base_yr=base_yr,
            curr_yr=curr_yr,
            value_start=0,
            value_end=1,
            yr_until_changed=yr_until_changed)

    elif diffusion == 'sigmoid':
        # Default sigmoid parameters
        simulation_year_p = diffusion_functions.sigmoid_diffusion(
            base_yr=base_yr,
            curr_yr=curr_yr,
            end_yr=yr_until_changed,
            sig_midpoint=0,
            sig_steeppness=1)
    else:
        sys.exit("Error: No diffusion option is selected")
    # --------------------------------------------------------------------
    # Calculate current year profile with base year and profile from 2015
    # --------------------------------------------------------------------

    # Get base year load profile
    for load_profile in load_profiles:
        if load_profile.name == 'av_lp_2015.csv':
            profile_yh_by = load_profile.shape_yh

    # Get future year load profile
    for load_profile in load_profiles:

        if charging_scenario == 'unsheduled':

            # Unsheduled load profile (same as base year)
            if load_profile.name == 'av_lp_2015.csv':
                profile_yh_ey = load_profile.shape_yh

        elif charging_scenario == 'sheduled':

            # Sheduled load profile
            if load_profile.name == 'av_lp_2050.csv':
                profile_yh_ey = load_profile.shape_yh
    
    if base_yr == curr_yr:
        profile_yh_cy = profile_yh_by
    elif curr_yr == yr_until_changed or curr_yr > yr_until_changed:
        profile_yh_cy = profile_yh_ey
    else:

        # Calculate difference between by and ey
        diff_profile = profile_yh_ey - profile_yh_by

        # Calculate difference up to cy
        diff_profile_cy = diff_profile * simulation_year_p

        # Add difference to by
        profile_yh_cy = profile_yh_by + diff_profile_cy

    assert round(np.sum(profile_yh_cy), 3) == 1

    # ----------
    # Plotting
    # ----------
    #from et_module import plotting_functions
    #fig_lp.plot_lp_dh(profile_yh_cy, day=2)

    # ------------------------------------
    # Disaggregate for every region
    # ------------------------------------
    for region_array_nr, region in enumerate(regions):

        # Sum total service demand to annual demand
        et_service_demand_y = np.sum(et_service_demand_yh[region])

        # Multiply the annual total service demand with yh load profile
        reg_profile_yh = et_service_demand_y * profile_yh_cy

        logging.debug(
            "Assinging new shape {}  {} {}".format(
                region, et_service_demand_y, np.sum(profile_yh_cy)))

        # Reshape (365 days, 24hours) into 8760 timesteps
        et_demand_yh[region_array_nr] = reg_profile_yh.reshape(8760)

    return et_demand_yh

def get_load_profiles(path):
    """Read in all load profiles from csv files and store in
    `LoadProfile`.

    Arguments
    =========
    path : str
        Path where load profiles are stored

    Returns
    =======
    load_profiles : list
        All load profiles objects
    """
    load_profiles = []

    # Name of load profiles to load
    names = [
        'av_lp_2015.csv',
        'av_lp_2050.csv']

    for name in names:

        # Create path to csv file
        path_to_csv = os.path.join(path, name)

        # Read in csv load profile
        lp_dh = read_load_shape(path_to_csv)

        lp_dh_p = lp_dh / 100 # convert percentage to fraction

        # Shape for every hour in a year (Assign same profile to every day)
        shape_yd = np.full((365), 1/365)

        # Shape for every hour in a year (365) * (24)
        shape_yh = shape_yd[:, np.newaxis]  * lp_dh_p

        # Create load profile
        load_profile = LoadProfile(
            name=name,
            year=name[-8:-4],
            shape_yd=shape_yd,
            shape_yh=shape_yh)

        load_profiles.append(load_profile)

    return load_profiles

def read_load_shape(path_to_csv):
    """This function reads in a load profile from
    a csv file of a single day.

    Arguments
    =========
    path_to_csv : str
        Path to csv file

    Returns
    =======
    shape_dh : array (24)
        Load profile
    """
    with open(path_to_csv, 'r') as csvfile:
        read_lines = csv.reader(csvfile, delimiter=',')
        _headings = next(read_lines) # Skip first row

        for row in read_lines:
            shape_dh = np.zeros((24), dtype=float)
            for cnt, row_entry in enumerate(row):
                shape_dh[int(_headings[cnt])] = float(row_entry)

    return shape_dh

class LoadProfile(object):
    """Class to store load profiles

    Arguments
    ----------
    name : str
        Name of load profile
    year : int
        Year of load profile
    shape_yd : array
        Yearly load profile
    shape yh : array
        Daily load profile

    Note
    ====
    -   `Yearly load profile (yd)` can be used to derive the energy demand
        of all days in year. This is achieved by multiplying total
        annual demand with this _yd array with the array shape (365)

    -   `Daily load profile (yh)` can be used to derive the energy demand
        of all hours in a year. This is achieved by multiplying total
        annual demand with the this _yh array with the array shape (365, 24).
    """
    def __init__(
            self,
            name,
            year,
            shape_yd,
            shape_yh
        ):
        """Constructor
        """
        self.name = name
        self.year = year
        self.shape_yd = shape_yd
        self.shape_yh = shape_yh