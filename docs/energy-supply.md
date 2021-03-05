# CGEN Combined Gas and Electricity Network Model

- [Model code](https://github.com/nismod/energy_supply) (not yet public)
- [Key reference](https://doi.org/10.1109/PTC.2019.8810641)

The energy supply model in the ITRC-MISTRAL programme is based on the Combined
Gas and Electricity Network model for Great Britain. [1,2] The ITRC-MISTRAL
energy supply model is rebuilt from the ground up and includes characterisation
of the energy supply system at both transmission and distribution scales. The
energy supply model performs operational analysis over multi-time periods
considering electricity, natural gas, hydrogen and heat supply systems and their
interactions. [3]

The model minimises total operational costs to meet energy demands across the
energy supply system. The operational costs of the energy system are derived
from energy supply, emissions and unserved energy. The cost minimisation is
subjected to constraints which are derived from the operational characteristics
of assets and the supply and demand balance of the energy system.

Energy transmission components in the model are connected to the electricity and
natural gas networks. These two transmission networks interact through gas fired
power generators. Energy resource supplies, generation technologies and networks
are explicitly modelled. Detailed modelling methods are used to represent
seasonal gas storage operation, variable generation of renewables and operation
of interconnectors. Energy supply at the transmission level meets demands from
large industrial consumers and energy flows to the distribution networks. The
figure below illustrates a stylised representation of the key electricity and
gas transmission system components modelled.

![Stylised representation of electricity and gas transmission systems.]()

Within energy distribution systems, integrated electricity, natural gas,
hydrogen and heat distribution systems are considered. To form the integrated
framework of various energy carriers (via energy conversion technologies) an
‘energy-hub’ concept is adopted. The energy hub utilises available regionally
distributed energy resources and transmission grid supplies to meet electricity,
natural gas and heat demands of residential and commercial consumers.
Constraints from each technology component and network energy flow capacities
are considered in the model. A simple illustration of an energy hub is shown in
the figure below.

![Energy hub representation of a distribution system.]()

The modelling approach in ITRC-MISTRAL offers a rich level of disaggregated
temporal and spatial representation of energy supply systems. This allows
detailed analysis of future energy supply systems under various strategies such
as integration of high levels of renewables, expansion of community and
distributed generation, benefits of electrical storage devices, greater consumer
participation and the challenge of decarbonising heat and mobility.

Key outputs from the model include the energy supply mix at both transmission
and distribution, total emissions from the electricity system and cost of
operation. Additionally, the model is also able to offer insights into the
impacts of user defined infrastructure expansion options.

### Modelling of the Oxford-Cambridge Arc

The energy supply model is utilised to analyse the Arc scenarios alongside
specific heat system strategies for the Oxford-Cambridge Arc. This region is
modelled using the existing spatial granularity 71 by which the distribution
regions are represented. The energy distribution regions are represented by 29
energy hubs as shown in the figure below. Three of these energy hubs (out of 29)
characterise energy systems within the Oxford- Cambridge Arc (1: Western-Oxford,
2: Central-Milton Keynes and 3: Eastern-Cambridge)

![Representation of energy distribution systems across GB and Oxford-Cambridge Arc region.]()

The energy distribution regions are connected to the transmission networks.

The figure below shows GB electricity and natural gas transmission network
representation within the energy supply model.

![GB electricity and natural gas transmission network representation within the energy supply model.]()

### Model setup

The GB electricity and gas transmission system and 26 energy hubs (i.e.
excluding the three energy hubs that represent the Oxford-Cambridge Arc region)
follow the generation and network ‘capacity pattern’ (out to 2050) as outlined
by the ‘Two Degrees’ Future Energy Scenarios (FES, National Grid 2019). To take
account of the differing demand requirements for the Arc scenarios the ‘capacity
pattern’ from the ‘FES two degrees’ scenario is sized linearly so that supply
matches demand whilst maintaining capacity margins.

The three energy hubs representing the Oxford-Cambridge Arc regions are
subjected to various supply side assumptions (technology, resource constraints)
to year 2050 which describe various pathways to meet energy demand. Table 3 of
the main report illustrates the strategies applied across the three Arc region
energy hubs. The strategies were chosen so that they cover a range of
possibilities across the Arc, from electrical domination to use of green gases
and district heat network solutions. Some of these strategies meet more
stringent emission targets than others (i.e. net zero). The heating demand is
projected by the energy demand model for years 2015, 2030 and 2050. From the
final heating demand, a maximum share is assigned to different technologies for
the supply of heat. This is reflected in the maximum installed heat supply
capacity for each technology within the Arc region. Distinct heat strategy
options were modelled. Technology uptake within these strategy options
considered key elements such as maturity, annual build rates, annual and peak
heat demand and capacity margin factors.

### Model simulation

Each energy supply model run performs operational analysis of the entire energy
system for a simulation year. Default model run setup of the energy supply model
performs analysis for the whole GB system. The outputs are recorded at regional,
and at transmission network level. Within each year, four seasons are modelled
with one representative week for each season using hourly time granularity.

### References

1. Chaudry, M., Jenkins, N. and Strbac, G. (2008). Multi-time period combined
   gas and electricity network optimisation. Electric Power Systems Research,
   78(7), pp. 1265–1279. doi: 10.1016/j.epsr.2007.11.002.
2. Chaudry, M., Jenkins, N., Qadrdan, M. and Wu, J. (2014). Combined gas and
   electricity network expansion planning, Applied Energy 113, pp. 1171-1187.
   10.1016/j.apenergy.2013.08.071.
3. Jayasuriya, L. et al. (2019). ‘Energy hub modelling for multi-scale and
   multi-energy supply systems’, 2019 IEEE Milan PowerTech, PowerTech 2019.
   IEEE, pp. 1–6. doi: 10.1109/PTC.2019.8810641.


## NISMOD Energy Supply data pack

[DAFNI dataset](https://facility.secure.dafni.rl.ac.uk/data/details?dataset_id=aa16e098-452b-496a-b3ae-dc95acd6959b&version_id=3d3380bc-2147-46a8-b1d6-74e755f3726b&metadata_id=134184ae-a086-4cf0-92c3-2ba9aa125c4e)

Version: v0.9.12

Includes model configuration for the electricity and gas network in the base
year (2015) and possible future interventions - generation, transmission,
interconnectors, gas storage and terminals, and heating supply technology
options.

Also contains parameters for model sensitivity analysis, historic and future
weather/climate time series for insolation and wind speed from the Met Office
and Weather@Home (aligned with the temperature time series used to model heating
energy demand), price scenarios, and spatial definitions for the energy hub
regions, gas nodes and bus bars.

Contains data covered by the Open Government Licence:
http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
Contains National Statistics data © Crown copyright and database right 2012.
Contains Ordnance Survey data © Crown copyright and database right 2012.

Contains historic weather station data derived from Met Office (2019): Met
Office MIDAS Open: UK Land Surface Stations Data (1853-current). Centre for
Environmental Data Analysis, date of citation.
http://catalogue.ceda.ac.uk/uuid/dbd451271eb04662beade68da43546e1

Contains future climate time series data derived from Guillod, B.P.; Jones,
R.G.; Kay, A.L.; Massey, N.R.; Sparrow, S.; Wallom, D.C.H.; Wilson, S.S. (2017):
Managing the Risks, Impacts and Uncertainties of drought and water Scarcity
(MaRIUS) project: Large set of potential past and future climate time series for
the UK from the weather@home2 model. Centre for Environmental Data Analysis,
17th April 2019. doi:10.5285/0cea8d7aca57427fae92241348ae9b03

All data compiled by Lahiru Jayasuriya and Modassar Chaudry, Cardiff University.
