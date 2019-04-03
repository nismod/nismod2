from copy import copy

from smif.data_layer.data_handle import ResultsHandle
from smif.decision.decision import RuleBased
from smif.data_layer.data_array import DataArray
from logging import getLogger
import pandas as pd
from typing import Dict, List

from digital_comms.fixed_network.interventions import decide_interventions
from digital_comms.fixed_network.adoption import update_adoption_desirability

from pytest import fixture

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
        annual_budget = 10000000.0 # type: float

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
            decisions = choose_interventions(rollout_results,
                                             annual_budget,
                                             self.current_timestep)
            self.satisfied = True

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
            decisions = choose_interventions(rollout_results,
                                             annual_budget,
                                             self.current_timestep)
            self.satisfied = True

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

        decision_data = decision_data.loc[list(self.interventions.keys())]

        return decision_data, total_cost

def choose_interventions(decision_data, annual_budget, timestep):

    best_by_exchange = _get_largest_in_each_exchange(decision_data, 'total_potential_bcr', 'exchanges')

    df = decision_data.loc[best_by_exchange]

    sorted_by_bcr = df.sort_values(
        by=['total_potential_bcr', 'rollout_costs'],
        ascending=[False, True])
    sorted_by_bcr['cumsum'] = sorted_by_bcr['rollout_costs'].cumsum()

    # Filter by available interventions
    chosen = sorted_by_bcr.where(sorted_by_bcr['cumsum'] <= annual_budget).dropna()

    decisions = []
    for row in chosen.itertuples(index=True, name='Intervention'):
        decisions.append({'name': row.Index,
                            'build_year': timestep})
    if decisions:
        return decisions
    else:
        return [{'name': '', 'build_year': ''}]

def _get_largest_in_each_exchange(df, metric, group):
    """Returns list of largest values of ``metric`` in each ``group``

    Arguments
    ---------
    df : pandas.DataFrame
        Expects columns exchanges and total_potential_bcr
    metric : str
        The decision metric that will be used to find the largest value
    group : str or list
        The column name or list of column names to group over

    Returns
    -------
    list of str
        The list of index names which can be used to filter the original dataframe
    """
    if isinstance(group, list):
        subset = []
        subset.extend(group).append(metric)
    else:
        subset = [group, metric]

    df = df[subset]

    largest = df.groupby(
        by=[group], as_index=False
        ).nth(0)
    return list(largest.index)


class TestInterventionChooser:

    @fixture(scope='function')
    def decision_data(self):

        columns = ['name', 'exchanges', 'technology', 'rollout_costs' ,'total_potential_bcr']
        data = [
            ('exchange_STBNMTH_fttdp', 'exchange_STBNMTH', 'fttdp', 133512, 91),
            ('exchange_EACAM_fttc', 'exchange_EACAM', 'fttc', 761070, 82),
            ('exchange_NEILB_fttc', 'exchange_NEILB', 'fttc', 631140, 46),
            ('exchange_NEILB_fttdp', 'exchange_NEILB', 'fttdp', 916095, 32)]

        df = pd.DataFrame(
            data=data, columns=columns)
        df = df.set_index('name')

        return df

    def test_get_largest_in_group(self, decision_data):

        expected = ['exchange_STBNMTH_fttdp',
                    'exchange_EACAM_fttc',
                    'exchange_NEILB_fttc']
        actual = _get_largest_in_each_exchange(decision_data, 'total_potential_bcr', 'exchanges')

        assert actual == expected

    def test_grouping(self, decision_data):

        actual = choose_interventions(decision_data, 133513, 2019)
        expected = [{
            'name': 'exchange_STBNMTH_fttdp',
             'build_year': 2019}]
        assert actual == expected