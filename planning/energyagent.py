from copy import copy

from smif.decision.decision import RuleBased
from smif.data_layer.data_array import DataArray
from logging import getLogger
import pandas as pd


class EnergyAgent(RuleBased):
    """A coupled power-producer/regulator decision algorithm for simulating
    decision making in an energy supply model

    EnergyAgent consists of two actors - a PowerProducer and a Regulator.

    The Regulator reviews the performance of the electricity system in the previous period
    against exogenously defined performance metric thresholds,
    such as emissions and capacity margin, and imposes constraints upon the
    available interventions through:
    - emission taxes
    - portfolio standards (e.g. % mandated to come from a generation type)

    In each timestep the PowerProducer assesses the current capacity shortfall
    against its projection of electricity demand and selects a portfolio of
    interventions using a heuristic based upon LCOE (levelised cost of electricity).

    """
    def __init__(self, timesteps, register):
        super().__init__(timesteps, register)
        self.model_name = 'energy_supply_optimised'
        self.logger = getLogger(__name__)

    @staticmethod
    def from_dict(config):
        timesteps = config['timesteps']
        register = config['register']
        return EnergyAgent(timesteps, register)

    def get_decision(self, data_handle):
        budget = self.run_critic(data_handle)
        decisions = self.run_actor(data_handle, budget)
        return decisions

    def run_critic(self, data_handle):
        """Simulates the operation of an energy regulator

        Arguments
        ---------
        data_handle
        """

        BUDGET = 9999

        iteration = data_handle.decision_iteration
        self.logger.debug("Current iteration is %s", iteration)
        if data_handle.current_timestep > data_handle.base_timestep:
            self.logger.debug("Current timestep %s is greater than base timestep %s",
                              data_handle.current_timestep, data_handle.base_timestep)
            cost = self.get_operating_cost(data_handle)
        else:
            cost = 0

        BUDGET -= cost

        self.satisfied = True

        return BUDGET

    def get_emissions(self, data_handle):
        output_names = ['e_emissions_eh', 'e_emissions']
        emissions = 0
        for output_name in output_names:
            da = self._get_results(data_handle, output_name)
            emissions += da.as_ndarray().sum()
            self.logger.debug("Retrieved emissions for %s: %s",
                            data_handle.previous_timestep,
                            output_name)
        return emissions

    def get_operating_cost(self, data_handle):
        output_names = ['total_opt_cost']
        total_opt_cost = 0
        for output_name in output_names:
            da = self._get_results(data_handle, output_name)
            total_opt_cost += da.as_ndarray().sum()
            self.logger.debug("Retrieved total operating cost for %s: %s",
                            data_handle.previous_timestep,
                            output_name)
        return total_opt_cost


    def _get_results(self, data_handle, output_name) -> DataArray:
        previous_timestep = data_handle.previous_timestep
        iteration = self._max_iteration_by_timestep[previous_timestep]
        return data_handle.get_results(model_name=self.model_name,
                                       output_name=output_name,
                                       timestep=previous_timestep,
                                       decision_iteration=iteration)

    def run_actor(self, data_handle, budget):
        """Simulates the operation of a power producer

        Arguments
        ---------
        data_handle: smif.data_layer.data_handle.DataHandle
        budget: float
        """
        cheapest_first = []
        for name, item in self.interventions.items():
            try:
                cap_cost = item['capital_cost']['value']
            except(KeyError):
                pass
            try:
                cheapest_first.append((name, float(cap_cost)))
            except(TypeError):
                cheapest_first.append((name, float("inf")))

        cheapest_first = sorted(cheapest_first, key=lambda x: float(x[1]), reverse=False)

        within_budget = []
        remaining_budget = copy(budget)
        for intervention in cheapest_first:
            self.logger.debug("Intervention is %s", intervention[1])
            if intervention[1] <= remaining_budget:
                within_budget.append({'name': intervention[0],
                                      'build_year': data_handle.current_timestep})
                remaining_budget -= intervention[1]

        self.logger.debug("Remaining budget: %s", remaining_budget)

        self.logger.debug("List of cheapest interventions: %s", cheapest_first)
        self.logger.debug(within_budget)
        return within_budget

def simple_lcoe(capital_cost, lifetime, capacity_factor, discount_rate):
    """
    sLCOE = {(overnight capital cost * capital recovery factor + fixed O&M cost )/(8760 * capacity factor)} + (fuel cost * heat rate) + variable O&M cost.

    """
    recovery_factor = capital_recovery_factor(discount_rate, lifetime)

    lcoe = ((capital_cost * recovery_factor) / (8760 * capacity_factor))

    return lcoe

def capital_recovery_factor(interest_rate, years):
    """Compute the capital recovery factor

    Computes the ratio of a constant loan payment to the present value
    of paying that loan for a given length of time. In other words,
    this works out the fraction of the overnight capital cost you need
    to pay back each year if you were to use debt to
    pay for the expenditure.

    Arguments
    ---------
    interest_rate: float
        The interest rate as a decimal value <= 1
    years: int
        The technology's economic lifetime

    """

    if float(interest_rate) == 0.:
        return 1. / years
    else:

        top = interest_rate * ((1 + interest_rate) ** years)

        bottom = ((1 + interest_rate) ** years) - 1

        total = top / bottom

        return total
