# Digital Communications

## Cambridge Digital Communications Assessment Model (cdcam)

Model code: [nismod/cdcam]](https://github.com/nismod/cdcam)

Model documentation:
[cdcam.readthedocs.io](https://cdcam.readthedocs.io/en/latest/index.html)

Key reference: Oughton, E.J., Russell, T., 2020. The importance of
spatio-temporal infrastructure assessment: Evidence for 5G from the
Oxford–Cambridge Arc. Computers, Environment and Urban Systems 83, 101515.DOI:
[10.1016/j.compenvurbsys.2020.101515](https://doi.org/10.1016/j.compenvurbsys.2020.101515)

For a full set of inputs and outputs:
- Oughton, Edward J., & Russell, Tom. (2019). cdcam (Version v1) [Data set].
  Zenodo. DOI: [10.5281/zenodo.3525286](http://doi.org/10.5281/zenodo.3525286)

## Longley-Rice Irregular Terrain Model (itmlogic)

Model code: [edwardoughton/itmlogic](https://github.com/edwardoughton/itmlogic)

Model documentation:
[itmlogic.readthedocs.io](https://itmlogic.readthedocs.io/en/latest/index.html)

Key reference: Oughton et al., (2020). itmlogic: The Irregular Terrain Model by
Longley and Rice. Journal of Open Source Software, 5(51), 2266, DOI:
[10.21105/joss.02266](https://doi.org/10.21105/joss.02266)

## Description

The 5G assessment model developed here can undertake system-level evaluation of
wireless networks, to help quantify the capacity, coverage and cost of different
5G deployment strategies. The capacity of a wireless network in a local area is
estimated using the density of existing cellular sites, the spectrum portfolio
deployed and the current technologies being used (either 4G or 5G for mass data
transfer). When supply- side infrastructure changes are made, such as building
new cellular sites or adding new spectrum bands, the incremental enhancement of
such decisions can be quantified in terms of the improved cellular capacity and
coverage, as well as in terms of the required investment.

The model used is a high-resolution spatially-explicit implementation of a
telecommunication Long Run Incremental Cost (LRIC) model. The model code, cdcam,
[1] is made available under an open-source license, unit-tested and thoroughly
documented online.

For 5G assessment, an infrastructure planning simulation model is developed
which consists of a set of interconnected software modules. The model represents
the key rollout period from 2020 to 2030, across spatial zones in the Arc, as
illustrated in the figure below.

![Digital communications system-level evaluation framework.]()

Necessary data inputs include spatially disaggregated demographic forecasts,
taken from SIMIM in this study, as well as forecasts on how per user data demand
will evolve in the future. Geospatial information is also required for site
locations, as well as data on the available spectrum portfolio by carrier
frequency, bandwidth and technology generation.

### Demand assessment

The mobile demand assessment module takes into account the two main drivers of
demand for cellular capacity: (i) the per user throughput rate and (ii) the
number of users in an area. The total number of active users accessing the
cellular network in an area is estimated and multiplied by the average user data
rate to obtain the total data demand being placed on the radio access network.

Per user data demand is taken from the widely-used Cisco traffic forecast. [2]
The adoption of unlimited data plans is likely to have a substantial impact on
data growth, with UK mobile traffic expected to grow at 38.5% Compound Annual
Growth Rate (CAGR) over the coming years.

Population scenarios at Local Authority District level are disaggregated to 9,000
Postcode Sectors using weights based on shares of 2011 census population. We model
a hypothetical operator with a market share of 25% of users, in line with the UK’s
Mobile Call Termination Market Review. [3] It is reasonable to expect that not all users will
access the network at once, and therefore an overbooking factor (OBF) of 50 is used,
which is standard practice for network dimensioning traffic throughput. [4] Smartphone
penetration in Britain is 80%, so only this proportion of the population is assumed to
access high capacity wireless services such as 4G LTE or 5G.

### Capacity assessment

The capacity assessment module is capable of quantifying cellular capacity
expansion using three methods, including improving spectral efficiency via new
technology generation, the provision of new spectrum bands and the deployment of
new cells to densify the network.

The mean spectral efficiency is obtained using a stochastic geometry approach
via the open-source python simulator for integrated modelling of 5G, pysim5G. [5]
First, pysim5G estimates the Signal to Interference plus Noise Ratio in
different urban and rural environment using industry-standard statistical
propagation models. Next, a spectral efficiency is allocated for the level of
received signal at the user, based on the ETSI coding and modulation lookup
tables for 5G. [6] The estimated cellular capacity can then be obtained for an
area by multiplying the spectral efficiency by the bandwidth of the carrier
frequency. To ensure a specific Quality of Service, the stochastic approach
allows the 10th percentile value to be extracted from the distribution of
simulation results for each frequency. This means that the network will be
upgraded to meet a desired user capacity at the cell edge with 90% reliability.

Physical sites data are taken from Ofcom’s Sitefinder data and updated to be
consistent with existing 4G coverage statistics released by Ofcom’s Connected
Nation report. In recent years, passive infrastructure sharing agreements have
essentially created two physical networks in the UK, the first between Vodafone
and O2 Telefonica (‘Cornerstone’) and the second between BT/EE and Hutchinson
Three. We consider the Vodafone and O2 Telefonica (‘Cornerstone’) sites as the
key supply-side input for (predominantly Macro Cell) sites. Representative site
locations are obtained by taking latitude and longitude coordinates for
individual cell assets, buffered by 80m, with the polygon centroid of touching
buffers forming an accurate location approximation. This results in
approximately 20,000 sites.

The statistics are disaggregated by ranking the revenue potential of each postcode
sector and calculating the cumulative geographic area covered using the expectation
that mobile networks operators (MNOs) rationally deliver 4G coverage to the highest
revenue sites first. This approach is consistent with how MNOs deploy new cellular
generations.

This assessment considers a hypothetical operator, representing a set of average
operator characteristics. A set of representative 4G LTE and 5G New Radio (NR)
carrier frequencies and bandwidths are tested in Frequency Division Duplex mode.
These frequencies consist of 10 MHz bandwidth for each of the 700 MHz, 800 MHz,
1.8 GHz and 2.6 GHz bands, 40 MHz bandwidth for 3.5 GHz, and 100 MHz bandwidth
for 26 GHz. The Total Cost of Ownership is estimated for each asset by
calculating the Net Present Value of the initial capital expenditure required in
the first year of deployment as a one-off cost, combined with the ongoing
operating expenditure over the lifetime of the asset (with opex being 10% of the
initial capex value for all active components, annually). A discount rate of
3.5% is used over a period of 10 years. This calculation does not consider price
trend changes and assumes a 10-year lifespan of Macro Cells. The total cost per
square kilometre for different network configurations can then be calculated
based on the density of assets by area. The costs per asset item are based on
the Mobile Call Termination model. [7]

### Fibre-to-the-Premises

The fixed broadband modelling assesses the cost of Fibre-to-the-Premises based
on density of premises in Output Areas under different urban development
scenarios. Openreach do not make detailed fixed broadband network data publicly
available to use for modelling. Therefore, the approach taken here is to use
network cost information from the report produced by Tactis & Prism for the
National Infrastructure Commission, as the analysts had access to the necessary
Openreach network data.

With this information, a cost modelling ‘geotype’ approach is used which is
based on the Office for National Statistics’ (ONS) urban-rural local authority
categories. A geotype is a group of geographical areas which have similar cost
properties. The six geotypes are based on a categorisation which ranges from the
densest urban conurbation, to remote rural areas.

To provide a geographically granular analysis, and to take the Arc scenarios
into account, premises estimates for 2050 are taken from the Urban Development
Model (UDM) outputs, where each hectare grid cell is either undeveloped or
developed at a given density. These results are then aggregated to the 11,085
ONS Output Areas within the Arc. Density of premises defines the geotype, and
therefore the cost per premises, for each Output Area under each urban
development scenario. The total cost estimates follow from number of premises
and cost per premises in each area.

The analysis script for this process is available within the
[nismod/digital_comms](https://github.com/nismod/digital_comms/) repository at
[`arc_fixed.py`](https://github.com/nismod/digital_comms/blob/master/scripts/arc_fixed.py).

### References

1. Oughton, E.J., and T. Russell (2019). The Cambridge Digital Communications
   Assessment Model v1.0.2. Available online: https://github.com/nismod/cdcam
   doi: 10.5281/zenodo.3583132.
2. Cisco (2017). VNI Mobile Forecast Highlights Tool.
3. Ofcom (2018). ‘Mobile Call Termination Market Review 2018-21: Final Statement
   – Annexes 1-15’.
4. Holma, Harri, and Antti Toskala, eds. (2012). LTE-Advanced: 3GPP Solution for
   IMT-Advanced. Chichester, UK: John Wiley & Sons, Ltd.
5. Oughton, E.J. (2019). ‘Python Simulator for Integrated Modelling of 5G
   (Pysim5g)’ Available online at https:// www.github.com/edwardoughton/pysim5g
6. European Telecommunications Standards Institute (2018). ‘ETSI TR 138 901
   V15.0.0 (2018-07). 5G; Study on Channel Model for Frequencies from 0.5 to 100
   GHz (3GPP TR 38.901 Version 15.0.0 Release 15)’.
7. Ofcom (2018). Mobile Call Termination Market Review 2018-21.
8. Oughton, E., Russell, T. 2020. The importance of spatio-temporal
   infrastructure assessment: Evidence for 5G from the Oxford–Cambridge Arc.
   Computers, Environment and Urban Systems, 83, 101515, DOI
   10.1016/j.compenvurbsys.2020.101515.


## cdcam data pack

[DAFNI dataset](https://facility.secure.dafni.rl.ac.uk/data/details?dataset_id=f44bece9-6822-4b7d-acbe-af18bb323702&version_id=7ead1555-b2e2-462c-b5e0-3085f2751957&metadata_id=147313e8-a5da-42ed-a59a-06953716e99f)

[DOI 10.5281/zenodo.3525286](https://doi.org/10.5281/zenodo.3525286)
