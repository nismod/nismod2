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
        annual_budget = 300000.0 # type: float

        decisions = [{'name': '',
                      'build_year': ''}] # type: List

        if (self.current_iteration > 1
            and self.current_timestep == data_handle.base_timestep):

            iteration = self.current_iteration - 1
            timestep = self.current_timestep

            state = data_handle.get_state(timestep, iteration)
            self.logger.debug("Updating state with %s", state)
            self.update_decisions(state)

            rollout_results, total_cost = self.get_previous_iteration_results(data_handle,
                                                                              timestep,
                                                                              iteration)
            decisions = self.choose_interventions(rollout_results, annual_budget)

        elif (self.current_iteration > 1
            and self.current_timestep > data_handle.base_timestep):

            iteration = self._max_iteration_by_timestep[data_handle.previous_timestep]
            timestep = data_handle.previous_timestep

            state = data_handle.get_state(timestep, iteration)
            self.logger.debug("Updating state with %s", state)
            self.update_decisions(state)

            rollout_results, total_cost = self.get_previous_iteration_results(data_handle,
             timestep,
            iteration)
            decisions = self.choose_interventions(rollout_results, annual_budget)

        return decisions

        # Get results from previous iteration

    def get_previous_iteration_results(self, data_handle, timestep, iteration):

        rollout_costs = data_handle.get_results(self.model_name,
                                                'rollout_costs',
                                                timestep,
                                                iteration)
        total_potential_bcr = data_handle.get_results(self.model_name,
                                                'total_potential_bcr',
                                                timestep,
                                                iteration)
        total_cost = data_handle.get_results(self.model_name,
                                                'total_cost',
                                                timestep,
                                                iteration)
        decision_data = rollout_costs.as_df() # type: pd.DataFrame
        decision_data = decision_data.merge(total_potential_bcr.as_df(),
                                            on=['exchanges', 'technology'])
        decision_data = decision_data.reset_index()
        decision_data['name'] = decision_data['exchanges'].str.cat(decision_data['technology'], sep="_")
        decision_data = decision_data.set_index('name')

        return decision_data, total_cost

    def choose_interventions(self, decision_data, annual_budget):

        self.logger.debug("Available interventions:\n%s", self.interventions)
        decision_data = decision_data.loc[self.interventions]

        sorted_by_bcr = decision_data.sort_values(by=['total_potential_bcr', 'rollout_costs'])
        sorted_by_bcr['cumsum'] = sorted_by_bcr['rollout_costs'].cumsum()

        self.logger.debug("Interventions sorted by bcr:\n%s", sorted_by_bcr)

        # Filter by available interventions
        chosen = sorted_by_bcr.where(sorted_by_bcr['cumsum'] <= annual_budget).dropna()

        self.logger.debug("Selected interventions sorted by bcr:\n%s", chosen)

        decisions = [{'name': '', 'build_year': ''}]
        for row in chosen.itertuples(index=True, name='Intervention'):
            decisions.append({'name': row.Index,
                              'build_year': self.current_timestep})
        self.satisfied = True

        return decisions