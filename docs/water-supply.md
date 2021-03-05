# WREW Water Resource System Model of England and Wales

- [Model code](https://github.com/nismod/water_supply) (not public)
- [Key reference](https://doi.org/10.1029/2020WR027187)

A water resource system model of England and Wales (WREW hereafter) has been
developed. [1] It includes all major water supply assets (reservoirs, boreholes,
transfers, water treatment works, pumped storage, desalination plants and river
abstraction points) that are connected into England and Wales’s wider water
network via any river or transfer of significance (i.e. > 2Ml/d). This includes
more than 90% of England and Wales’s population and water demand, and more than
80% of their combined land area.

WREW is the product of an extensive collaboration led by the University of Oxford
between a range of stakeholders: England and Wales’s environmental agencies,
UK-based water consultancies, the Water UK council, and all of England and
Wales’s water supply companies. The water system formulation in the model is
based on communications with, and datasets provided by, the above stakeholders.
This formulation includes: pipe capacities, treatment works capacities,
reservoir capacities, abstraction and operational licence conditions,
operational preferences, control curves, system connectivity, and asset
locations where necessary (e.g. for river abstractions or boreholes). Beyond its
use for this research, WREW will become a key tool for England’s Environment
Agency (EA) that can provide them with a model-based national perspective on
droughts, policy reform and infrastructure planning.

WREW is simulated at a daily time-step using the WATHNET water resource
simulation software. [2] Every time-step, WATHNET solves a mass balance
optimization problem that allocates water between model nodes, via arcs, under
both constraints inherent to mass balance (e.g. nonzero flows and storages) and
constraints set out by the water system’s formulation (e.g. pipe capacities and
minimum required river flows). The solver minimizes a set costs associated with
each model arc, performed by Network Linear Programming. These costs do not
represent literal economic costs but are instead used to direct the model’s
behaviour according to operator preferences. For example, if one source is
preferable to another its cost is set lower than the other, if one is preferable
during summer and one during winter the arc costs are updated to reflect this.
Arcs and nodes have their own scripts for which custom rules can be set,
allowing incredibly detailed implementation of operator preferences and complex
licences. To enable the solver to cope with this high level of customisation,
which may introduce non-linearity or discontinuity, it is run repeatedly every
time-step to enable navigation of the decision space. WATHNET is also highly
efficient in its simulation; WREW contains 1252 nodes and 1756 arcs yet one year
of simulation at daily timestep takes around only 2 minutes on a 3.6GHz
processor. For context, the similar sized CALVIN water resource simulation model
runs at around 10 minutes per year at a monthly timestep on a 2 GHz PC [3] (we
note this is for context and not comparison since CALVIN’s simulation philosophy
is inherently different; it is a perfect foresight optimization model that
represents operation as a release sequence as defined in Dobson et al. (2019).
[4]

As one would expect from any national scale water resource simulation model, a
range of assumptions (beyond those described in the following sections) have
gone into its creation. These can be separated into modelling assumptions that
have been informed by water company instruction/practice, and assumptions that
are primarily the result of data/information availability or the scope of work.

Company informed assumptions include:

- Aggregation of some reservoirs that supply a single treatment works,
- Representing redistribution of water in the unmodelled distribution network by
  allowing multiple sources/transfers to deliver water to the same demand node,
- The omission of small sources, particularly those with <1Ml/d – which is
  WATHNET’s solver accuracy.

Instead, assumptions that are the result of limited data/scope are:

- Instantaneous travel time along arcs (with the exception of a few large
  aqueducts whose flow travel times are known),
- Reservoirs have zero evaporation (with the exception of a few large surface
  area reservoirs for which an evaporation relationship is well described), we
  note here that the UK experiences low rates of evaporation and that most
  reservoirs have evaporation lower than WATHNET’s solver accuracy of 1Ml/d,
- Water quality is not modelled but instead assumed that it will always be
  acceptable provided that volumetric licence conditions and minimum required
  flow volumes are met,
- The decision making of water companies during a drought is highly complex due
  to a range of pressures that cannot be modelled, we have worked with water
  companies to represent these in an acceptable way but the full range of
  options available under drought conditions was considered outside the scope of
  this work.

### References

1. Dobson, B., Coxon, G., Freer, J., Gavin, H., Mortazavi‐Naeini, M., & Hall, J.
   W. (2020). The spatial dynamics of droughts and water scarcity in England and
   Wales. Water Resources Research, 56, e2020WR027187.
   https://doi.org/10.1029/2020WR027187
2. Kuczera, G. (1992). Water supply headworks simulation using network linear
   programming. Advances in Engineering Software, 14(1), 55–60.
3. Harou, J. J., Medellín-Azuara, J., Zhu, T., Tanaka, S. K., Lund, J. R.,
   Stine, S., ... Jenkins, M. W. (2010). Economic consequences of optimized
   water management for a prolonged, severe drought in California. Water
   Resources Research, 46(5).
4. Dobson, B., Wagener, T., & Pianosi, F. (2019). An argument-driven
   classification and comparison of reservoir operation optimization methods.
   Advances in Water Resources, 128(October 2018), 74–86.
