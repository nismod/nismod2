from copy import copy

from smif.data_layer.data_handle import ResultsHandle
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

    def get_decision(self,
                     data_handle : ResultsHandle) -> List[Dict]:
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
        interventions = self.interventions # type: List
        print(interventions)

        if data_handle.current_timestep > data_handle.base_timestep:
            iteration_of_prev_timestep = self._max_iteration_by_timestep[data_handle.previous_timestep]
            rollout_costs = data_handle.get_results(self.model_name,
                                                'rollout_costs',
                                                self.previous_timestep,
                                                iteration_of_prev_timestep)
            rollout_bcr = data_handle.get_results(self.model_name,
                                                'rollout_bcr',
                                                self.previous_timestep,
                                                iteration_of_prev_timestep)
            total_cost = data_handle.get_results(self.model_name,
                                                'total_cost',
                                                self.previous_timestep,
                                                iteration_of_prev_timestep)

            # Get the technology strategy parameter - this should consist of a string
            # which describes the policy and
            technology = 'fttdp'
            policy = 's1_market_based_roll_out'

            # suggested_interventions = decide_interventions(
            #     interventions,
            #     data_handle.current_timestep,
            #     technology,
            #     policy,
            #     data_handle.get_parameter('annual_budget').data,
            #     adoption_cap,
            #     data_handle.get_parameter('subsidy').data,
            #     data_handle.get_parameter('telco_match_funding').data,
            #     data_handle.get_parameter('service_obligation_capacity').data,
            # )
            # print(suggested_interventions)



        return [{'name': '',
                 'build_year': data_handle.current_timestep }]