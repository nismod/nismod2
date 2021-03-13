# HIRE High-Resolution Energy Demand Model

- Model code: [nismod/energy_demand](https://github.com/nismod/energy_demand)
- Model documentation: [ed.readthedocs.io](https://ed.readthedocs.io/en/latest/documentation.html)
- Key references:
  - Eggimann, S., Hall, W.J., Eyre, N. (2019): A high-resolution spatio-temporal
    energy demand simulation of large-scale heat pump diffusion to explore the
    potential of heating demand side management. Applied Energy, 236, 997–1010.
    DOI:
    [10.1016/j.apenergy.2018.12.052](https://doi.org/10.1016/j.apenergy.2018.12.052)
  - Eggimann, S., Usher, W., Hall, J.W. and Eyre, N. How weather affects energy
    demand variability in the transition towards sustainable heating, Energy,
    195 (2020) 116947. DOI:
    [10.1016/j.energy.2020.116947](https://doi.org/10.1016/j.energy.2020.116947)

For a list of model inputs, parameters and outputs, see:
- [Energy demand (constrained)](./energy_demand_constrained_details.html)
- [Energy demand (unconstrained/optimised)](./energy_demand_unconstrained_details.html)

HIRE allows the simulation of long-term changes in energy demand patterns for
the residential, service and industry sector on a high temporal and spatial
scale. National end-use specific energy demand data is disaggregated on local
authority district level and a bottom-up approach is implemented for hourly
energy demand estimation for different fuel types and end uses.Future energy
demand is simulated based on different socio-technical scenario assumptions such
as technology efficiencies, changes in the technological mix per end use
consumptions or behavioural change. Energy demand is simulated in relation to
changes in scenario drivers of the base year. End-use specific socio-technical
drivers for energy demands modelled where possible on a household level.

The methodology is published in [1].

For further model documentation, see [2]

### References

1. Eggimann, S., Hall, W.J., Eyre, N. (2019): A high-resolution spatio-temporal
   energy demand simulation of large-scale heat pump diffusion to explore the
   potential of heating demand side management. Applied Energy, 236, 997–1010.
   https://doi.org/10.1016/j.apenergy.2018.12.052.
2. Eggimann, S., Usher, W., Russell, T. (2019) HIRE documentation. Available
   online: https://ed.readthedocs.io/en/latest/documentation.html

## NISMOD Energy Demand data

[DAFNI dataset](https://facility.secure.dafni.rl.ac.uk/data/details?dataset_id=180c33ea-592c-473e-b54b-692c2cc534dd&version_id=f63c24ec-4262-4f88-ac1c-28fd47345de1&metadata_id=8c90791b-e00b-4ff2-87e3-1e9e9c5f9b48)

Version: v0.9.12

Data required by NISMOD Energy Demand model (HIRE).

Includes Local Authority District region definitions, hourly interval
definitions, technology, efficiency, end-use and service parameters to explore
changing energy demand, historic temperature time series from the Met Office,
scenarios of future temperature derived from Weather@Home climate time series
(aligned with the wind speed and insolation time series used to model renewables
in energy supply), base year (2015) national and subnational energy consumption
estimates, load profiles derived from the DECC Household Electricity Survey and
Carbon Trust Advanced Metering Trial, and Office of National Statistics data on
base year population and floor area.

Contains data covered by the Open Government Licence:
http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
Contains National Statistics data © Crown copyright and database right 2012.
Contains Ordnance Survey data © Crown copyright and database right 2012.

Contains national energy consumption estimates for 2015, derived from BEIS
(2016): Energy consumption in the UK (ECUK). London, UK. Retrieved from:
https://www.gov.uk/government/collections/energy-consumption-in-the-uk

Contains load profiles derived from DECC (2014) Household Electricity Survey.
Retrieved
from:https://www.gov.uk/government/collections/household-electricity-survey

Contains data derived from Carbon Trust Advanced Metering Trial licensed for
academic research purposes, © Carbon Trust 2006, accessible at
https://data.ukedc.rl.ac.uk/browse/edc/efficiency/residential/Buildings/AdvancedMeteringTrial_2006

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

All data compiled by Sven Eggimann, University of Oxford.

Please refer to and cite Eggimann, S., Hall, W.J., Eyre, N. (2019): A
high-resolution spatio-temporal energy demand simulation of large-scale heat
pump diffusion to explore the potential of heating demand side management.
Applied Energy, 236, 997–1010. https://doi.org/10.1016/j.apenergy.2018.12.052.
