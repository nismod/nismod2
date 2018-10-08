from energyagent import EnergyAgent, capital_recovery_factor, simple_lcoe
from unittest.mock import Mock

from pytest import fixture, approx


class TestEnergyAgent():

    @fixture(scope='function')
    def agent(self):
        timesteps = [2010, 2015, 2020]
        register = {'intervention_a': {'capital_cost': {'value': 100}},
                    'intervention_b': {'capital_cost': {'value': 99}}}

        agent = EnergyAgent(timesteps, register)
        return agent

    @fixture(scope='function')
    def mock_handle(self):
        mock_handle = Mock()
        mock_handle.current_timestep = 2010
        mock_handle.base_timestep = 2010
        return mock_handle

    def test_get_decisions(self, agent, mock_handle):

        decisions = agent.get_decision(mock_handle)

        assert decisions == [{'name': 'intervention_b', 'build_year': 2010}]

    def test_run_power_producer_no_budget(self, agent, mock_handle):
        """With no budget left, no decisions should be returned
        """

        budget = 0
        actual = agent.run_power_producer(mock_handle, budget)
        expected = []
        assert actual == expected

    def test_run_power_producer_infinite_budget(self, agent, mock_handle):
        """With infinite budget, the power producer can build everything
        """

        budget = float("inf")
        actual = agent.run_power_producer(mock_handle, budget)
        expected = [
            {'name': 'intervention_a', 'build_year': 2010},
            {'name': 'intervention_b', 'build_year': 2010}]
        assert actual == expected

class TestMethods():

    def test_capital_recovery_factor(self):
        assert capital_recovery_factor(0., 10.) == 0.1
        assert capital_recovery_factor(0.07, 30.) == approx(0.08058640)

    def test_lcoe(self):

        actual = simple_lcoe(1000, 30, 0.8, 0.07)
        expected = approx(0.011499201414256734)
        assert actual == expected