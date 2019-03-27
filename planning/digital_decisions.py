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
        self.model_name = 'digital_comms_fixed_network'
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

        Notes
        -----
        The procedure for choosing interventions is

        - retrieve the rollout costs and cost-benefit ratio from the previous iteration
        - rank the interventions according to the cost-benefit ratio
        - choose the subset of most beneficial interventions that do not exceed
          budget

        """
        annual_budget = 150000.0 # type: float

        decisions = [{'name': '',
                      'build_year': ''}] # type: List

        interventions = self.interventions # type: List
        print(interventions)

        if (self.current_iteration > 1
            and self.current_timestep == data_handle.base_timestep):

            iteration = self.current_iteration - 1

            timestep = self.current_timestep

            decisions = self.choose_interventions(data_handle,
                                                  timestep,
                                                  iteration,
                                                  annual_budget)

        elif (self.current_iteration > 1
            and self.current_timestep > data_handle.base_timestep):

            iteration = self._max_iteration_by_timestep[data_handle.previous_timestep]

            timestep = data_handle.previous_timestep

            decisions = self.choose_interventions(data_handle,
                                                  timestep,
                                                  iteration,
                                                  annual_budget)

        return decisions

        # Get results from previous iteration

    def choose_interventions(self, data_handle, timestep, iteration, annual_budget):

        rollout_costs = data_handle.get_results(self.model_name,
                                                'rollout_costs',
                                                timestep,
                                                iteration)
        rollout_bcr = data_handle.get_results(self.model_name,
                                                'rollout_bcr',
                                                timestep,
                                                iteration)
        total_cost = data_handle.get_results(self.model_name,
                                                'total_cost',
                                                timestep,
                                                iteration)
        self.logger.debug(rollout_costs.as_df())
        self.logger.debug(rollout_bcr.as_df())
        self.logger.debug(total_cost.as_df())

        decision_data = rollout_costs.as_df() # type: pd.DataFrame
        decision_data = decision_data.merge(rollout_bcr.as_df(),
                                            on=['exchanges', 'technology'])

        self.logger.debug(decision_data)

        sorted_by_bcr = decision_data.sort_values(by=['rollout_bcr', 'rollout_costs'])
        sorted_by_bcr['cumsum'] = sorted_by_bcr['rollout_costs'].cumsum()

        self.logger.debug(sorted_by_bcr)

        # sorted_by_bcr = sorted_by_bcr.set_index(['exchanges', 'technology'])
        chosen = sorted_by_bcr.where(sorted_by_bcr['cumsum'] <= annual_budget).dropna()

        self.logger.debug(chosen)

        decisions = [{'name': '', 'build_year': ''}]
        for row in chosen.itertuples(index=True, name='Intervention'):
            print(row)
            decisions.append({'name': "_".join(row.Index),
                                'build_year': data_handle.current_timestep})
        self.satisfied = True

        return decisions