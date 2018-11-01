from copy import copy

from smif.decision.decision import RuleBased


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
        self.model_name = 'energy_supply'

    @staticmethod
    def from_dict(config):
        timesteps = config['timesteps']
        register = config['register']
        return EnergyAgent(timesteps, register)

    def get_decision(self, data_handle):
        budget = self.run_regulator(data_handle)
        decisions = self.run_power_producer(data_handle, budget)
        return decisions

    def run_regulator(self, data_handle):
        """
        data_handle
        """

        budget = 100

        iteration = data_handle.decision_iteration
        if data_handle.current_timestep > data_handle.base_timestep:
            self.logger.debug("Current timestep %s is greater than base timestep %s",   data_handle.current_timestep, data_handle.base_timestep)
            output_name = 'total_opt_cost'
            cost = data_handle.get_results(model_name='energy_supply_toy',
                                           output_name=output_name,
                                           timestep=data_handle.previous_timestep,
                                           decision_iteration=iteration)
            budget -= cost

        return budget

    def run_power_producer(self, data_handle, budget):
        """
        data_handle
        budget : float
        """
        cheapest_first = []
        for name, item in self.register.items():
            try:
                cap_cost = item['capital_cost']['value']
            except(KeyError):
                pass
            try:
                cheapest_first.append((name, float(cap_cost)))
            except(TypeError):
                cheapest_first.append((name, float("inf")))

        sorted(cheapest_first, key=lambda x: float(x[1]), reverse=False)

        within_budget = []
        remaining_budget = copy(budget)
        for intervention in cheapest_first:
            if intervention[1] <= remaining_budget:
                within_budget.append({'name': intervention[0],
                                      'build_year': data_handle.current_timestep})
                remaining_budget -= intervention[1]

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