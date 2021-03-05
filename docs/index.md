# NISMOD National Infrastructure Systems Model

NISMOD (National Infrastructure Systems Model) is an integrated model of
infrastructure systems, developed as part of the
[ITRC/MISTRAL](https://www.itrc.org.uk/) project.

NISMOD v2 has several components:
- infrastructure sector models
- an integration framework, [smif](https://smif.readthedocs.io/en/latest/)
- configuration to link the models into a system-of-systems model, [nismod2](https://github.com/nismod/nismod2/)
- scenario, narrative and planning data to run linked model runs
- (for some models) internal model data, used by the model but not exposed as
  part of the system-of-systems configuration

## Energy Demand

HIRE (HIgh-Resolution Energy demand model) simulates energy demand for the
United Kingdom at an hourly / Local Authority District scale.

Future energy demand is simulated based on different scenario data and
socio-technical drivers such as technological efficiencies, changes in the
technological mix of an end use, consumption and behavioural change.

Scenario data includes population, regional Gross Value Added, residential and
commercial floorspace, and temperature.

Outputs are energy demand per sector (residential/commercial/industrial), per
LAD, per hour, per fuel. These do not include transport energy demand, which
is provided by the NISMOD transport model.

[More details on energy demand](./energy-demand.html)

## Energy Supply

The NISMOD Energy Supply model provides the capability to perform integrated
analyses of the whole energy system in Great Britain from supply sources,
generation, transmission, distribution and end-use.

The model is built on an optimisation framework. It performs integrated optimal
operation of the energy system across electricity, gas, heat, and hydrogen
networks.

Inputs include demand for each fuel, as well as wind speed, insolation,
interconnector prices, and biomass and solid waste available as feedstock. For
transport end uses, both electricity demand and battery storage capacity are
provided with the option to allow V2G/G2V.

Outputs include electricity generation by technology, both transmission grid
connected and local (heat, renewables) within the energy hubs, gas usage by
source, storage levels, fresh water demand and emissions.

[More details on energy supply](./energy-supply.html)

## Transport

NISMOD v2 Transport Model is a national-scale (Great Britain) transport model
developed to support policy making regarding the future infrastructure.

It forecasts the impact of various endogenous and exogenous factors on transport
demand and capacity utilisation, following an elasticity-based simulation
methodology.

The model consists of three submodels covering the following modes of transport:
road (passenger and freight vehicle flows), rail (total station usage), and air
(domestic and international passenger movements).

[More details on transport](./transport.html)

## Water

The WREW water resource system model of England and Wales includes major water
supply assets (reservoirs, boreholes, transfers, water treatment works, pumped
storage, desalination plants and river abstraction points).

The model simulates water supply at a daily timestep, testing potential system
interventions under scenarios of future flows and future demand.

Key outputs include water supplied, shortfall and storage at the network node
level (demand zone / reservoir), along with the days where the model would
introduce varying levels of restrictions on public supply.

[More details on water](./water-supply.html)

## Digital Communications

The cdcam model can undertake system-level evaluation of wireless networks, to
help quantify the capacity, coverage and cost of different 5G deployment
strategies.

The capacity of a wireless network in a local area is estimated using the
density of existing cellular sites, the spectrum portfolio deployed and the
current technologies being used (either 4G or 5G for mass data transfer).

When supply- side infrastructure changes are made, such as building new cellular
sites or adding new spectrum bands, the incremental enhancement of such
decisions can be quantified in terms of the improved cellular capacity and
coverage, as well as in terms of the required investment.

[More details on digital communications](./digital.html)
