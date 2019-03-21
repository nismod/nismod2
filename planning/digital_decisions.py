from copy import copy

from smif.decision.decision import RuleBased
from smif.data_layer.data_array import DataArray
from logging import getLogger
import pandas as pd
from typing import Dict, List

from digital_comms.fixed_network.interventions import decide_interventions
from digital_comms.fixed_network.adoption import update_adoption_desirability


class DigitalDecisions(RuleBased):

    def __init__(self, timesteps, register):
        super().__init__(timesteps, register)
        self.model_name = 'digital_comms'
        self.logger = getLogger(__name__)

    @staticmethod
    def from_dict(config):
        timesteps = config['timesteps']
        register = config['register']
        return DigitalDecisions(timesteps, register)

    def get_decision(self, data_handle) -> List[Dict]:
        """Return decisions for a given timestep and decision iteration

        Parameters
        ----------
        results_handle : smif.data_layer.data_handle.ResultsHandle

        Returns
        -------
        list of dict

        Examples
        --------
        >>> register = {'intervention_a': {'capital_cost': {'value': 1234}}}
        >>> dm = DecisionModule([2010, 2015], register)
        >>> dm.get_decision(results_handle)
        [{'name': 'intervention_a', 'build_year': 2010}])
        """

        # Get the technology strategy parameter - this should consist of a string
        # which describes the policy and
        technology = 'fttdp'
        policy = 'baseline'

        # -----------------------
        # Get scenario adoption rate
        # -----------------------
        # annual_adoption_rate = data_handle.get_data('adoption').data

        distributions = data_handle.get_data('distributions')

        annual_adoption_rate = 40

        # get adoption desirability from previous timestep
        adoption_desirability = [
            distribution for distribution in self.system._distributions
            if distribution.adoption_desirability]

        total_distributions = [distribution for distribution in self.system._distributions]

        adoption_desirability_percentage = (
            len([dist.total_prems for dist in adoption_desirability]) /
            len([dist.total_prems for dist in total_distributions]) * 100)

        percentage_annual_increase = round(float(annual_adoption_rate - \
            adoption_desirability_percentage), 1)

        # update the number of premises wanting to adopt (adoption_desirability)
        distribution_adoption_desirability_ids = update_adoption_desirability(
            self.system._distributions, percentage_annual_increase)

        # -----------------------
        # Run fixed network model
        # -----------------------
        # get total adoption desirability for this time step (has to be done after
        # system.update_adoption_desirability)
        adoption_desirability_now = [
            dist for dist in self.system._distributions if dist.adoption_desirability]

        total_adoption_desirability_percentage = round(
            (len([dist.total_prems for dist in adoption_desirability_now]) /
            len([dist.total_prems for dist in total_distributions]) * 100), 2)

        # calculate the maximum adoption level based on the scenario, to make sure the
        # model doesn't overestimate
        adoption_cap = len(distribution_adoption_desirability_ids) + \
            sum(getattr(distribution, technology) for distribution in self.system._distributions)

        interventions = decide_interventions(
            self.system,
            data_handle.current_timestep,
            technology,
            policy,
            data_handle.get_parameter('annual_budget').data,
            adoption_cap,
            data_handle.get_parameter('subsidy').data,
            data_handle.get_parameter('telco_match_funding').data,
            data_handle.get_parameter('service_obligation_capacity').data,
        )
        return interventions