# NISMOD v2 Transport Model (Road and Rail)

- Model code: [nismod/transport](https://github.com/nismod/transport)
- Key reference: Lovric, M., Blainey, S., & Preston, J. (2018). A conceptual
  design for a national transport model with cross-sectoral interdependencies.
  Transportation Research Procedia, 27, 720-727

For a list of model inputs, parameters and outputs, see:
- [Road](./transport_details.html)
- [Rail](./rail_details.html)
- [Energy-transport](./et_module_details.html)

NISMOD v2 Transport Model [1] is a national-scale (Great Britain) transport model
developed to support policy making regarding future infrastructure. It forecasts
the impact of various endogenous and exogenous factors on transport demand and
capacity utilisation, following an elasticity-based simulation methodology
similar to the original ITRC model (NISMOD v1). The new model, however, is
explicitly network-based, in that that the demand is assigned to the transport
network to obtain more accurate predictions of travel times, travel costs and
capacity utilisation.

### Road transport model

The NISMOD v2 Transport Model predicts vehicle demand (inter-zonal flows) for
passenger and freight vehicles, and stochastically simulates road traffic on all
major UK roads including A-roads and motorways. The number of lanes on each road
segment has been estimated by map-matching AADF count point locations to the
OpenRoads major road network. This has allowed a distinction between single and
dual carriageway A-roads, which are then assumed to have 1 and 2 lanes per
direction, respectively.

It is currently the only national-scale road traffic model capable of
routing-based network assignment and provisioning a national-scale
origin-destination matrix (on TEMPRo & LAD spatial zoning levels), while
achieving a respectable match with AADF traffic counts, total vehicle
kilometres, expected number of car trips, and the observed trip length
distribution from the National Travel Survey. The freight model has been
modelled after the DfT’s 2006 Base-Year Freight Matrices model, which includes
traffic flows for freight vehicles (vans, rigid HGVs, and articulated HGVs)
between local authority districts (LADs), sea ports, selected airports, and
major distribution centres. The accuracy of the freight model is mostly limited
by the spatial zoning system (LAD).

Demand prediction for the transport model is given by an elasticity-based model
that can predict future vehicle flows from exogenous (scenario-based) changes in
population and GVA, and endogenously calculated changes in inter-zonal travel
time and travel cost (but also dependent on exogenous interventions such as new
road development and congestion charging policies).

Congested travel times on individual road links have been modelled separately
for each hour of the day, using the speed-flow curves estimated on English roads
(DfT’s 2005 FORGE model), the overcapacity formula from WebTAG, and the
passenger car unit (PCU) concept to capture different vehicle sizes.

The network assignment exists in two versions and has been implemented using
state- of-the-art routing algorithms. The routing version uses an A* heuristic
search algorithm to find the fastest path between two locations using congested
link travel times, while the route-choice version uses an advanced
discrete-choice model (path-size logit) to choose the optimal path based on
distance, travel time, travel cost (fuel and road tolls), and the number of
intersections.

The route-choice version of the network assignment uses a pre-generated route
set, which consists of more than 90 million different route options, enabling
the national- scale assignment to run within minutes, despite each individual
vehicle trip being simulated separately (including time of day choice, engine
type choice, route choice). The model can assess different scenarios of fuel
efficiency and engine type market share (i.e. internal combustion engines on
petrol, diesel, LPG, hydrogen or CNG; hybrid EVs on petrol or diesel; plug-in
hybrid EVs on petrol or diesel; fuel cell EVs on hydrogen, and battery EV). This
scenario analysis can be used to test policies such as the fossil fuel
phase-out.

Electricity and fuel consumption are calculated using the four-parameter formula
from WebTAG. Behavioural assumptions are made for plug-in hybrid EVs
(electricity on urban, fuel on rural road links).

Interventions such as new road development, road expansion with new lanes, and
congestion charging zones can be dynamically implemented in each simulated year.
The model can output various metrics at the road link level (e.g. road capacity
utilisation, peak hour travel times), zonal level (e.g. vehicle kilometres, EV
electricity consumption), inter-zonal level (e.g. predicted vehicle flows,
average travel times, average travel costs) and national level (e.g. total CO₂
emissions, total energy consumptions). The outputs are in csv and shapefile
format, allowing them to be visualised with a software of choice.

### Rail model

The NISMOD v2 Transport Model also includes a national-scale rail model for
predicting future station usage, using base year data for 3054 stations covering
National Rail, London Underground, Docklands Light Railway, London Trams
(previously Croydon Tramlink), Manchester Metrolink, and Tyne & Wear (Newcastle)
Metro.

The demand model is elasticity-based, and can predict station usage (entry +
exit) from exogenous inputs including: population, GVA, rail fare index,
generalised journey time (GJT) index and car trip costs (which can be provided
as an input or calculated from the outputs of the NISMOD road model). Demand
elasticities of rail fares and GJT vary between different areas of the country
(London Travelcard, South-East, PTE, other).

The model capabilities include an assessment of building new rail stations in
future years.

### References

1. Lovric, M. et al. (2019). ‘NISMOD Transport v2.2.1’ Available online:
   https://github.com/nismod/transport doi: 10.5281/zenodo.3583128


## NISMOD Transport data pack

[DAFNI dataset](https://facility.secure.dafni.rl.ac.uk/data/details?dataset_id=dbfe6814-3fd3-4e94-8c30-ccfec60c9989&version_id=df234857-a622-4b83-bec1-c72b1c7ed8b6&metadata_id=2cbc52e7-d987-48ac-8e38-9f2da417ad35)

Version: v2.3.0

Contains data required by the NISMOD Transport model.

Includes the strategic road network (motorways and A roads), TEMPRO zone
definitions, stations, modelled passenger and freight origin-destination
matrices, modelled route options, future interventions (congestion charging,
lane expansions, new road links, new stations), parameters and scenarios for
fuel efficiency, costs, trip rates, time of day distributions for trips, future
composition of the road fleet (vehicle and engine type), and default model
elasticity parameters (for time, cost, population and GVA).

Contains data covered by the Open Government Licence:
http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
Contains National Statistics data © Crown copyright and database right 2012.
Contains Ordnance Survey data © Crown copyright and database right 2012.

Road network and AADF traffic counts data are derived from Department for
Transport GB Road Traffic Counts: -
https://data.gov.uk/dataset/208c0e7b-353f-4e2d-8b7a-1a7118467acc/gb-road-traffic-counts

Railway stations are largely derived from the NaPTAN extract, supplemented with:
- estimates of station usage and NLC codes:
  estimates-of-station-usage-2015-16.xlsx
  https://dataportal.orr.gov.uk/statistics/usage/estimates-of-station-usage/
- DLR station usage data FOI request: DLR Passenger Journeys 2013 2015.xlsx
  https://www.whatdotheyknow.com/request/up_to_date_dlr_entry_exit_statis
- DLR NLC codes came with this FOI: https://www.whatdotheyknow.com/request/station_codes
- Tyne & Wear (Newcastle) Metro (synthetic NLCs): Metro Station Patronage FOI
  request 06 06 2017 Final data.xlsx
  https://www.whatdotheyknow.com/request/tyne_and_wear_passenger_numbers
- Manchester Metrolink (synthetic NLCs): DSD Report 1878 Rail and Metrolink
  Section 2015.xlsx (the first link)
  https://gmtu.gov.uk/reports/transport2015.htm
- Croydon Tramlink (synthetic NLCs): Counts By Stop 2014 FOI Request.xls
  https://www.whatdotheyknow.com/request/dlr_and_tramlink_passenger_numbe

Particularly for model calibration, origin-destination matrix generation and
route-set generation, we acknowledge the use of the IRIDIS High Performance
Computing Facility, and associated support services at the University of
Southampton.

All data compiled by Milan Lovric and Simon Blainey, University of Southampton.
