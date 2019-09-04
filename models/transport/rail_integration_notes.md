# Rail model integration in NISMOD2 using the `smif` framework

Author: Thibault Lestang
Created: 2019-07-25 Thu 17:12

## Parameters

The rail model model depends on the following parameters
- The elasticities for the rail demand model
- A flag indicating whether to use the output of the road model for car journey costs data
- A flag indicating whether to compute all years between the base year and predicted year

### 4.1 Elasticities

The rail demand model depends on four variables

- Population in origin zone(`POPULATION`)
- Gross Value Added per head in origin zone (`GVA`)
- Average travel time between origin and destination zones (`TIME`)
- Average rail trip cost between origin and destination (`COST_RAIL`)
- Average car trip cost (fuel) between origin and destination (`COST_CAR`)

Additionally, the value of the elasticity for each variable depends on the area

- London Travel card (`LT`)
- South East (`SE`)
- Passenger Transport Executives (`PTE`)
- Other areas (`OTHER`)

The elasticities data was provided by the rail model in a format that is readable with smif,
provided the definition of two dimensions

- `variables` (Coordinates: `POPULATION`, `GVA`, `TIME`, `COST_RAIL`, and `COST_CAR`)
- `area` (Coordinates: `LT`, `SE`, `PTE`, `OTHER`)

The definition of both dimensions can be found in `config/dimensions/`.

From a smif point of view, the 20 elasticities values are described by one unique
bi-dimensional parameter `elasticities`

```yaml
name: rail
...
parameters:
  - name: elasticities
    dims:
      - variables
      - area
    description: Elasticities for rail demand model
    dtype: float
    default: default_rail_elasticities.csv
```

Default elasticities values can be found in `data/parameters/`.

```csv
variables,area,elasticities
POPULATION,LT,1
POPULATION,SE,1
...
GVA,LT,0.55
GVA,SE,0.55
GVA,PTE,0.55
...
COST_CAR,OTHER,0.12
```

### 4.2 Rail model flags

The behaviour of the rail model can be modified by setting the value of two Boolean flags in
the `config.properties` file.

```
FLAG_USE_CAR_COST_FROM_ROAD_MODEL = false
FLAG_PREDICT_INTERMEDIATE_YEARS_RAIL = false
```

Two Boolean parameter are thus defined in the smif configuration of the rail sector model

```yaml
name: rail
...
parameters:
  - name: use_car_cost_from_road_model
    description: Whether to use output of road model for car costs
    dtype: bool
    default: default_rail_flags.csv
  - name: predict_intermediate_rail_years
    description: Whether to predict all years between base year and predicted year
    dtype: bool
    default: default_rail_flags.csv
```

Both default values are contained in one single data file -
`data/parameters/default_rail_flags.csv`

```
use_car_cost_from_road_model,predict_intermediate_rail_years
False,False
```

## 5 Input data

### 5.1 Population and G.V.A.

#### 5.1.1 Data

Population and G.V.A inputs had already been integrated in the smif framework as part of a
previous integration work for the road part of the transport model (T. Russell). Population and
G.V.A are provided by scenarios `population` and `gva`, respectively. Scenario data for both
inputs was already available in `data/scenarios/`.

Both population and G.V.A inputs are uni-dimensional, the dimension being the L.A.D. and
associtaed coordinates the LAD codes.

Data thus takes the form
`data/scenarios/population/pop-baseline16_econ-c16_fuel-c16/population__lad.csv`

```
timestep,lad_uk_2016,population
2015,E06000001,93192.39038189998
2015,E06000002,140288.541157
...
2016,E06000001,93400.0324534
2016,E06000002,140300.011773
```


#### 5.1.2 Integration in smif

Population and G.V.A data is provided for the whole United Kingdom, totalling 391 L.A.Ds. As a
result, input data must be filtered down to either GB LADs or Southampton area LADs.

This is achieved by introducing an additional sector model `extract_southampton_scenarios` (or
`extract_gb_scenarios`) that takes the full LAD dimension–with 391 coordinates– as an input.
The filter sector model then outputs the reduced data along a reduced dimension which
coordinates are the codes of the 380 LADs in Great Britain - extract_Southampton_scenarios.yml

```yaml
name: extract_Southampton_scenarios
path: ./models/extract.py
classname: FilterAdaptor
inputs:
  - name: gva
    dims:
      - lad_uk_2016
    unit: £
    dtype: float
outputs:
  - name: gva
    dims:
      - lad_southampton
    unit: GBP
    dtype: float
```

The output of the filter sector model is then an input for the actual rail model:

```yaml
name: rail_southampton
description: Test model for transport
sector_models:
  - rail_southampton
  - extract_southampton_scenarios
scenarios:
  - socio-economic # Provides the population data
narratives: []
scenario_dependencies:        # Population from socio-economic
  - source: socio-economic    # scenario to filter model
    source_output: population
    sink: extract_southampton_scenarios
    sink_input: population
...
model_dependencies:
  - source: extract_southampton_scenarios  # From filter model to
    source_output: population              # sector model
    sink: rail_southampton
    sink_input: population
    timestep: PREVIOUS
...
```


### 5.2 Car Zonal Journey Costs

#### 5.2.1 Data

Similarly to population and G.V.A., the zonal journey cost is an uni-dimensional input with
LADs codes as a dimension. Data is provided by the transport model in a single
`carZonalJourneyCosts.csv` file, usually located in
`data/transport/southampton/data/csvfiles/`. The file contains one row for each year, and one
column per LAD. For instance, for the Southampton area, it shows - carZonalJourneyCosts.csv
(southampton data)

```
year,E06000045,E07000086,E07000091,E06000046
2015,10.55,12.25,13.35,16.57
2016,10.55,12.25,13.35,16.57
...
```

Such file can be converted in a smif readable scenario data file using the script
`convert_car_zonal_journey_costs.py` located in `utilities/transport/`. Be sure to indicate the
correct dimension name for the column name, for instance `'lad_southampton'` for the
Southampton data.

#### 5.2.2 Integration

Journey costs scenario data has been generated using the `carZonalJourneyCost.csv` file for the
full GB test. Data does not include Northern Ireland and is only provided for the 380 LADs in
Great Britain.

Journey costs input data is therefore filtered down to Southampton LADs for the Southampton
test case, using the `extract_southampton_scenarios` filter model as above. However for the ful
GB test case, input data for the rail model is directly the scenario output -
config/sector_models/extract_southampton_scenarios.yml

```yaml
name: extract_southampton_scenarios
...
inputs:
  - name: car_zonal_journey_costs
    dims:
      - lad_gb_2016
    dtype: float
    unit: £
...
outputs:
  - name: car_zonal_journey_costs
    dims:
      - lad_southampton
    dtype: float
    unit: £
...
```


### 5.3 Rail journey fares and rail journey times

#### 5.3.1 Data

Both rail journey times and rail journey fares are uni-dimensional inputs, with rail stations
as a dimension. The dimension coordinates (the rails stations indexes) are the _National
Location Codes_ (NLCs).

Journey fares and times are provided for either Great Britain or the Southampton area, in data
files `railStationJourneyFares.csv` and `railStationGeneralisedJourneyTimes.csv`, respectively.
Smif-ready scenario data can be generated from these files using scripts
`convert_rail_station_journey_fares.py` and `convert_rail_station_journey_fares.py`.

Scenario data has been generated for Great Britain, located in

- `data/scenarios/rail_station_journey_times.csv`
- `data/scenarios/rail_station_journey_fares.csv`

#### 5.3.2 Integration in smif

Both inputs are provided by a common scenario `rail_journey_times_fares` -
config/scenarios/rail_journey_times_fares.yml

```yaml
name: rail_journey_times_fares
description: Journey times and fares for transport rail model
provides:
  - name: rail_journey_fares
    dims:
      - NLC_gb
    dtype: float
    unit: £
  - name: rail_journey_times
    dims:
      - NLC_gb
    dtype: float
    unit: h
variants:
  - name: baseline
    description: Journey times and fares for transport rail model
    data:
      rail_journey_fares:  rail_station_journey_fares.csv
      rail_journey_times: rail_station_journey_times.csv
```

As scenario data files contains data for the stations in Great Britain (dimension `NLC_gb`),
scenario outputs feed directly into the rail model inputs. However, filtering is necessary for
the Southampton test case.

#### 5.3.3 Hack: Journey times for the Southampton area test case

At the moment, the journey times data file provided for the Southampton area contains stations
that are **not present** in the file containing data for Great Britain. As a result, the data
for the Southampton test case cannot be obtained by simple filtering of the GB data.

Therefore, a specific scenario for the Southampton test case has be defined:
`rail_journey_times_fares_soton`. It outputs journey times with a dimension that is consistent
with the current data file for Southampton journey times. The corresponding dimension is called
`NLC_southampton_generalised`. In addition, the scenario configuration file points to a
specific data file

- `data/scenarios/rail_station_generalised_journey_times_soton.csv`

The input for journey fares (`rail_journey_fares`) is not affected and is kept identical to the
original scenario provided data for Great Britain -
config/scenarios/rail_journey_times_fares_soton.yml

```yaml
name: rail_journey_times_fares_soton
provides:
  - name: rail_journey_fares
    # Same as GB scenario #
  - name: rail_journey_times
    dims:
      - NLC_southampton_generalised
    dtype: float
    unit: h
...
```

For the Southamtpon test case, journey fares data is thus filtered down to Southampton stations
using the filter model, and journey times is directly obtained from the specific scenario.

### 5.4 Trip rates

#### 5.4.1 Data

The trip rate is a scalar input (no dimension). Its value is given in the `railTripRates.csv`
data file, with one column per year. This file can thus directly used in `smif` as scenario
data - data/transport/southampton/data/csvfiles/railTripRates

```yaml
timestep,rail_trip_rates
2015,1
2016,1
...
```


#### 5.4.2 Integration

Rail trip rates are provided by a scenario `rail_trip_rates`. Scenario data is already provided
by the transport model in the correct format, and the `railTripRates.csv` file was just renamed
into

- `data/scenarios/rail_trip_rates.csv`

### 5.5 Station usage (yearly and daily)

### 5.6 Base year rail usage

The rail model predicts stations usage for future years, based on the usage (or _demand_) for
the base year.

The base year demand must therefore be provided as an initial input to the rail model,
indicating yearly and daily usage for each of rail stations considered in the model run. These
numbers act as a basis for the computation of station usage for the subsequent simulated years.

The base year rail demand numbers are provided to the rail model _via_ a csv data file,
typically called `baseYearRailUsage.csv`, or `baseYearRailDemand.csv`.

This files contains as many rows as there are active rail stations in the base year, as well as
several columns for various stations properties:

```
NLC,Mode,Station,NaPTANname,Easting,Northing,YearUsage,DayUsage,RunDays,LADcode,LADname,Area
375,NRAIL,Energlyn_&_Churchill_Park,Energlyn_&_Churchill_Park_Rail_Station,314957,187866,74206,204.4242424,363,W06000018,Caerphilly,OTHER
500,TUBE,Acton_Town,Acton_Town_Underground_Station,519446,179637,6235045,17129.24451,364,E09000009,Ealing,LT
```

**Remark**

Base year data files provided by the rail model contains white spaces, which makes processing
the text they contain difficult. As a result white spaces have been replaced by underscores '_'
in station names.

The main purpose of this file is to provide the base year yearly and daily usage (`YearUsage`
and `DayUsage`) for the rail model.

#### 5.6.1 The station usage scenario

Base year station usage data is usually provided to the rail model through the base year rail
usage file. In NISMOD however, station usage data is provided by a smif scenario
`station_usage`. This scenario provides both daily and yearly stations usage for the base year.
`station_usage` scenario.

*Data*

Scenario data could be obtained by extracting the daily and yearly usage from the base year
rail usage file for each rail station, resulting in two data files

- `data/scenarios/rail_day_usage.csv`
- `data/scenarios/rail_year_usage.csv`

This can be achieved, for instance, using the following shell script

```
# Extract base year rail demand from baseYearUsage.csv provided by rail model
base_year_usage_file=data/transport/gb/data/csvfiles/baseYearRailUsage.csv
day_usage_file=data/scenarios/rail_day_usage.csv
if [ -f $day_usage_file ]; then
    rm -i $day_usage_file
fi
base_year=2015
for line in $(cat $base_year_usage_file)
do
    echo $base_year,$(echo $line | cut -d, -f1,7) >> $day_usage_file
done
# Fix first line with correct column names
sed -i "1s/.*/timestep,NLC_gb,day_usage/" $day_usage_file
```

Both inputs are one-dimensional, whith the station NLCs as coordinates:

```
# data/scenarios/rail_day_usage.csv
timestep,NLC_gb,day_usage
2015,375,204.4242424
2015,500,17129.24451
...
```

Note that, in practice, the station usage scenario data can only contain data for the base
year. At the moment, only station usage data for the year 2015 is available.

Station usage data for future years is one of the outputs of the rail model.

*Integration*

The `station_usage` scenario provides both `day_usage` and `year_usage` for all stations
considered in the Great Britain test case. In this case the scenario outputs are inputs of the
rail model. For the Southamtpon test case, station usage output is filtered down to stations in
the Southampton area, using the filter model, as already described above.

#### 5.6.2 Base year rail usage data file

The base year rail usage file can be constructed by adding daily and yearly usage to the data
describing rail interventions. Station usage for the base year is obtained from the station
usage scenario, for each of the stations considered. Station usage numbers are then paired with
the corresponding intervention (based on the NLC) to build the base year rail usage file.

## 6 Output data

The rail model outputs two csv files

- `predictedRailDemand.csv`
- `zonalRailDemand`

The two files consist of several columns

- A first columns indicating the year of the current timestep (predicted year)
- A second column for the dimension:
    - Station NLC for `predictedRailDemand.csv`
    - LAD code for `zonalRailDemand.csv`
- Several columns for different properties, of which only a subset are actual computed output data.

From smif, the rail model has 6 uni-dimensional outputs, which value can be found in a unique
column of either `predictedRailDemand.csv` or `zonalRailDemand.csv`.

smif output                    | output file               | column in output file
-------------------------------|---------------------------|-----------------------
`year_stations_usage`          | `predictedRailDemand.csv` | `YearUsage`
`day_stations_usage`           | `predictedRailDemand.csv` | `DayUsage`
`total_year_zonal_rail_demand` | `zonalRailDemand.csv`     | `yearTotal`
`avg_year_zonal_rail_demand`   | `zonalRailDemand.csv`     | `yearAvg`
`total_day_zonal_rail_demand`  | `zonalRailDemand.csv`     | `dayTotal`
`avg_day_zonal_rail_demand`    | `zonalRailDemand.csv`     | `dayTotal`


## 7 Interventions

Interventions for the transport model are described in specific `*.properties` files. They
indicate the start year, end year, type of intervention..etc

```
# Example winslowRailStation.properties
type = NewRailStation
startYear = 2030
endYear = 2100
NLC = 500000
mode = NRAIL
station = Winslow
naPTANname = N/A
easting = 476600
northing = 228300
yearUsage = 100000
dayUsage = 275.482093664
runDays = 363
LADcode = E07000004
LADname = Aylesbury Vale
area = SE
```

Interventions for the model run must be listed in the `config.properties` file.

**Important**: Paths to rail model interventions files must be name following the template
`railInterventionFileX` where `X` is an arbitrary identifier (typical a number).

```
# Example config.properties
....
# interventions
railInterventionFile0 = data/transport/southampton/input/newSouthamptonStation.properties
railInterventionFile1 = data/transport/southampton/input/myOtherNewStation.properties
...
```


### 7.1 Intervention data for smif

Intervention data is generated for **every** stations considered in the model. For every
station, the intervention data contains _almost_ the same information required in the
intervention `*.properties` files. The intervention data is contained in a csv data file of the
type

```
NLC,name,type,technical_lifetime_value,technical_lifetime_units,mode,station,naPTANname,easting,northing,runDays,LADcode,LADname,area
375,newEnerglyn_&_Churchill_Park_NRAIL,NewRailStation,100,y,NRAIL,Energlyn_&_Churchill_Park,Energlyn_&_Churchill_Park_Rail_Station,314957,187866,363,W06000018,Caerphilly,OTHER
500,newActon_Town_TUBE,NewRailStation,100,y,TUBE,Acton_Town,Acton_Town_Underground_Station,519446,179637,364,E09000009,Ealing,LT
```

- Note that this data does **not** contain yearly and daily usage numbers, which are provided
  by by the `station_usage`. They are gathered in the smif wrapper and added to the
  `*.properties` file describing the intervention.
- The intervention data does not contain the start and end year, but instead the _lifetime_
  (`technical_lifetime_value`) of the interventions. This is because, using smif, the start
  year of interventions are given in the strategies data file. See
  [https://smif.readthedocs.io/en/latest/decisions.html](https://smif.readthedocs.io/en/latest/decisions.html)
  for more information on how interventions are handled in smif.

In this way, _any_ station listed in the smif intervention file can be built as part of an
intervention. The smif wrapper is in charge of writing the `*.properties` for the stations to
be built on the current year, adding the corresponding station usage from the `station_usage`
scenario, as well, as computing the start and end years base on the lifetime of the
intervention.

### 7.2 Generating intervention data for smif

The intervention data file used by smif can be generated by extracting the relevant columns
from the base year rail usage data csv file. The resulting file will however only list the
stations older than the base year–indeed that base year usage file dos not list future
stations. Therefore, any potential future station must be added to the intervention data file.

Intervention data for older stations can be generated using the following shell script

- `utilities/transport/write_rail_interventions_from_base_year_data.sh`

resulting in

```
# data/interventions/transport_rail.csv
NLC,name,type,technical_lifetime_value,technical_lifetime_units,mode,station,naPTANname,easting,northing,runDays,LADcode,LADname,area
375,newEnerglyn_&_Churchill_Park_NRAIL,NewRailStation,100,y,NRAIL,Energlyn_&_Churchill_Park,Energlyn_&_Churchill_Park_Rail_Station,314957,187866,363,W06000018,Caerphilly,OTHER
...
...
300092,newWythenshawe_Town_Centre_LRAIL,NewRailStation,100,y,LRAIL,Wythenshawe_Town_Centre,Wythenshawe_Town_Centre_(Manchester_Metrolink),382552,387050,364,E08000003,Manchester,PTE
```

Potential future stations must be added to this file. For instance, in order to build the
Winslow rail staion, the corresponfing intervention data is appended

```
# data/interventions/transport_rail.csv
NLC,name,type,technical_lifetime_value,technical_lifetime_units,mode,station,naPTANname,easting,northing,runDays,LADcode,LADname,area
375,newEnerglyn_&_Churchill_Park_NRAIL,NewRailStation,100,y,NRAIL,Energlyn_&_Churchill_Park,Energlyn_&_Churchill_Park_Rail_Station,314957,187866,363,W06000018,Caerphilly,OTHER
...
...
300092,newWythenshawe_Town_Centre_LRAIL,NewRailStation,100,y,LRAIL,Wythenshawe_Town_Centre,Wythenshawe_Town_Centre_(Manchester_Metrolink),382552,387050,364,E08000003,Manchester,PTE
500000,newWinslowRailStation_NRAIL,NewRailStation,100,y,NRAIL,New Winslow,N/A,476600,228300,363,E07000004,Aylesbury Vale,SE
```


#### 7.2.1 Hack: Interventions with the same name

**Problem**: Several stations can host several transport modes of transport: national rail,
local rail, tube (in London..). As a result several stations in the base year rail usage file
can have the same `name`, but a different `Mode`. Because of the way intervention data is
generated for smif, several interventions can end up with the same name, which is not allowed.

**Workaround**: When generating intervention data, the mode is appended to the intervention
name.

```
# Example
newSouthamptonStation ----> newSouthamptonStation_NRAIL
```

## 8 The rail model smif wrapper

The main task in integrating a model into the smif framework is to write the corresponding
wrapper class, derived from the abstract `SectorModel` class. The smif wrapper class is
responsible for the pre-processing of model inputs and post-processing of model outputs, as
well as the actual running of the model iteself. For instance, the rail model wrapper is
responsible for writing the `config.properties` configuration file required for the rail model
to run. It is also responsible for generating the input files for car journey costs, journey
times and fares, population.. etc.

Most of the rail wrapper methods are implemented in the `BaseTransportWrapper` class that
directly inherits from `SectorModel`.

Information specific to the test case (full G.B. or Southampton area, for instance) is
specified in test case specific classes derived from `BaseTransportWrapper`. For example

```python
class SouthamptonRailTransportWrapper(BaseTransportWrapper):
    """Wrap the rail model, in 'southampton' configuration
    """
    _config_filename = 'run_config_rail_southampton.ini'
    _template_filename = 'rail_southampton-config.properties.template'
class RailTransportWrapper(BaseTransportWrapper):
    """Wrap the rail model, in 'southampton' configuration
    """
    _config_filename = 'run_config_full.ini'
    _template_filename = 'rail-config.properties.template'
```

The central method in the `SectorModel` class is `simulate`, which is executed at every
timestep. It takes a smif `DataHandle` object as an argument, which gives access to all the
data necessary to run the model–provided the configuration was done correctly. Among other
things, the `DataHandle` gives access to input data from scenarios or other models, model
parameters or interventions to be performed in the current timestep.

The simulate method for the `BaseTransportWrapper` is as follows

```python
def simulate(self, data):
...
    self._current_timestep = data.current_timestep
    self._set_parameters(data)
    self._set_inputs(data)
    self._set_properties(data)
    self._run_model_subprocess(data)
    if self._current_timestep > data.base_timestep:
  self._set_outputs(data)
```

Methods `_set_parameters`, `_set_inputs`, `_set_properties` are responsible for getting input
values, parameters values, current interventions from the `DataHandle` and writing input files
to disk for the rail model to read.

### 8.1 Template rail model configuration file

Transport wrapper classes write the `config.properties` file based on a template. This template
specifies the name of the input, parameter and output files. The paths to these files, the
values of the boolean parameters as well as the list of interventions is set by the smif
wrapper in the `BaseTransportWrapper._set_properties` method. Because the names of the data
files are specified in the template, it is important that the names used in the wrapper classes
methods are consitent with the names in the template.

Templates are located in `models/transport/templates/`.

### 8.2 Rail model parameters

Elasticities are processed in the `_set_parameters` method. The values can just be loaded from
the data handle and written as such to a CSV file with the correct name provided in the
template `config.propeties` file.

The two boolean flags `FLAG_USE_CAR_COST_FROM_ROAD_MODEL` and
`FLAG_PREDICT_INTERMEDIATE_YEARS_RAIL` are set in the `_set_properties` method

```python
def _set_properties(self, data_handle):
    ....
    # read config as a Template for easy substitution of values
    with open(path_to_config_template) as template_fh:
  config = Template(template_fh.read())
    config_str = config.substitute({
  'use_car_cost_from_road_model': \
      bool(data_handle.get_parameter('use_car_cost_from_road_model').data),
  'predict_intermediate_rail_years': \
      bool(data_handle.get_parameter('predict_intermediate_rail_years').data),
  })
    # Write config file to disk
    with open(self._config_path, 'w') as template_fh:
  template_fh.write(config_str)
```


### 8.3 Rail model inputs

All inputs of the rail model are one-dimensionnal inputs, except from the rail trips rate.

#### 8.3.1 1D outputs

One dimensionnal inputs are processed using the `_set_1D_inputs` method defined as follows

```python
def _set_1D_input(self, data_handle, input_name, filename,dtype=None):
  """Get one dimensional model input from data handle and write to input file
  Arguments
  ---------
  data_handle: smif.data_layer.DataHandle
  input_name: str
  filename: str
  dtype: type [optional]
  """
```

This method loads the data for the input `input_name` for both the current and previous
timestep and writes it in one single file `filename`. The type of the data can be specified by
providing a `dtype` argument. This for instance the case when processing the `population`
input:

```python
    def _set_inputs(self, data_handle):
  """Get model inputs from data handle and write to input files
  """
  self._set_1D_input(data_handle, 'population', 'population.csv', dtype=int)
...
```


#### 8.3.2 Trip rate

In contrast to other inputs, the trip rate is an unidimensionnal input. More importantly, the
rail model requires trip rate numbers for every year between the base year and the predicted
year, unlike other inputs like population that are only required at the previous predicted
year. Trip rate input data is processed in a separate method `_set_trip_rates`

```python
def _set_trip_rates(self, data):
    """Get trip rates input from data handle and write to input file
    Arguments
    ---------
    data_handle: smif.data_layer.DataHandle
    """
```

This method load trip rate data from the data handle for every year between
`data.base_timestep` and `data.current_timestep` and concatenate values to build the CSV input
file for the rail model to read.

### 8.4 Rail model outputs

The rail model wrapper reads the rail model output files `predictedRailDemand.csv` and
`zonalRailDemand.csv` and load the relevant data into the data handle for the corresponding
sector model outputs (see section [6](#org99f2060)).

The `=BaseTransportWrapper._set_1D_output()` is in charge of loading output data from an output
file to the data handle

```python
def _set_1D_output(self, data_handle, output_name, filename, cols):
    """Get one dimensional model input from data handle and write to input file
    Arguments
    ---------
    data_handle: smif.data_layer.DataHandle
    output_name: str
    filename: str
    cols: dict - Labels of the columns to keep.
      Keys are label in the ouput file.
      Values are label in data_handle.
    """
```

To each of the rail model outputs (as defined in the sector model configuration file)
correspond a unique column in one of the output file from the rail model. Firstly, the output
file `filename` is read into a DataFrame. All columns except the output dimension and the ouput
itself are dropped from the DataFrame, and the renaming columns are renamed according the
output and dimension names provided by the smif configuration of the rail model

```python
filename = self._output_file_path(filename)
df = pd.read_csv(filename)
df = df.loc[:,cols.keys()].rename(columns=cols)
```

The output data is then turned into a numpy array and loaded into the data handle for the
corresponding output `output_name`.

### 8.5 Interventions

Current rail interventions data is loaded from the data handle in the `_set_properties` method.

The method `DataHandle.get_current_interventions()` returns a dictionary keyed by intervention
name. It returns all interventions built until the current timestep (included), including
initial conditions. From the point of view of the rail model, rail stations built before the
base year (initial conditions) should not be described by a intervention `*.properties` file,
because they are already described in the base year rail usage file.

The list of current interventions is thus filtered down to interventions built _from_ the base
year using `_filter_interventions`. Provided the data handle, this method returns the list of
interventions built _strictly before_ (init. conditions) of _from_ the base year onwards.

Each intervention in the list is then written as a `*.properties` that can be read by the rail
model.

```python
def _set_properties(self, data_handle):
...
# Discard initial conditions
interventions = self._filter_interventions(data_handle)
for i, intervention in enumerate(interventions):
    # Write .properties intervention file for the rail model
    fname = self._write_rail_intervention(intervention, data_handle)
    # Update list of interventions to be written in config.properties
    intervention_files.append("railInterventionFile{} = {}".format(i, fname))
....
```

Eventually the list of interventions is injected in the template `config.properties` file

```python
# read config as a Template for easy substitution of values
with open(path_to_config_template) as template_fh:
    config = Template(template_fh.read())
    config_str = config.substitute({
  'intervention_files': '\n'.join(intervention_files),
  })
    with open(self._config_path, 'w') as template_fh:
  template_fh.write(config_str)
```


### 8.6 Base year rail usage

The smif wrapper is also responsible for writing the base year rail usage file. This is
achieved by the `BaseTransportWrapper` method `_set_base_year_demand`. The base year rail usage
data can be formed by combining intervention data for stations built before the base year, as
well as corresponding daily and yearly station usage from the `station_usage` scenario.

Intervention data for stations predating the base year is obtained through

```python
interventions = self._filter_interventions(data_handle, future=False)
```

Data is then converted as a Pandas DataFrame, from which columns not appearing in the base year
rail usage file are dropped:

```python
base_df = pd.DataFrame.from_dict(interventions)
base_df = base_df.rename(columns={'NLC': 'NLC_gb'}).set_index('NLC_gb')
base_df.index.names = ['NLC']
cols_to_drop = ['technical_lifetime_units',
    'technical_lifetime', 'name', 'type', 'build_year']
base_df = base_df.drop(cols_to_drop, axis=1)
```

The next step is to gather daily and yearly usage from the `station_usage` scenario.

```python
baseyear_day_usage = data_handle.get_data("day_usage",
              timestep=data_handle.base_timestep)
baseyear_year_usage = data_handle.get_data("year_usage",
                timestep=data_handle.base_timestep)
```

The base year rail usage file structure can then be obtained by concatenating the three
DataFrames

```python
base_df = pd.concat([base_df, baseyear_day_usage, baseyear_year_usage], axis=1,
            join_axes=[df.index])
```

Note: The `station_usage` data dimension includes all rail stations, including ones to be built
as interventions in the future. The `base_df` only lists stations predating the base year,
hence the argument `join_axes = [df.index]`

#### 8.6.1 Hack: Columns in DataFrame must be renamed

The rail model expects most of the keys in intervention `*.properties` files to begin with a
lower case character. However the columns in the base year rail usage file must begin with an
upper case charater.

The smif intervention data file (`data/interventions/transport_rail.csv`) has columns names
that begin with lower case characters as well: `station`, `area`, `easting`… etc.

The columns in the base year rail usage DataFrame must therefore be renamed prior to writing
the CSV file

```python
# rename columns to meet rail model's expectations
columns_names = {
    'mode': 'Mode',
    'station': 'Station',
    'naPTANname': 'NaPTANname',
    'easting': 'Easting',
    ....
}
base_df = df.rename(columns=columns_names)
```

The last step is to reorder the columns. If the columns are in the wrong order, the rail model
will not throw an error, however the predicted rail usage data will only contain future
stations. Only future station data can be read because interventions data have the columns in
the correct order. In contrast the base year demand file may be read incorrectly.

```python
cols = ['Mode', 'Station', 'NaPTANname', 'Easting', 'Northing',
  'YearUsage', 'DayUsage', 'RunDays', 'LADcode', 'LADname', 'Area']
base_df = base_df[cols]
```

Eventually the base year rail usage input file is written

```python
# Write base year rail demand csv file
df.to_csv(os.path.join(self._input_dir, 'baseYearRailDemand.csv'))
```

## 9 Validation

### 9.1 Create several model runs from one year to another

  Full-scale (Great Britain) rail model run. Intervention: Winslow station in 2018 Model runs:
- `[X]` 2015 -> 2017 Winslow station is not built
- `[X]` 2015 -> 2018 Winslow station is built
- `[ ]` 2018 -> 2030
- `[ ]` 2030 -> 2050
- `[X]` Duplicate model run `rail_full_test.yml` into 4 model runs for each experiement.
    - `rail_full_2015_2017.yml`
    - `rail_full_2015_2018.yml`
    - `rail_full_2018_2030.yml`
    - `rail_full_2030_2050.yml`
- `[X]`
    Change build year in `transport_build_winslow.csv` (2015 -> 2018)

    ```
    name,build_year
    newWinslowRailStation_NRAIL,2018
    ```


### 9.2 Convert predicted rail demand data into input `station_usage` data.

Predicted rail demand has the form

```
year,NLC,Mode,..,YearUsage,DayUsage,RunDays,LADcode,LADname,Area
2020,5494,NRAIL,...,126148,347.5151515151515,363,E06000046,Isle_of_Wight,SE
2020,5504,NRAIL,...,69920,192.61707988980717,363,E06000046,Isle_of_Wight,SE
2020,5525,NRAIL,...,1811694,4990.892561983471,363,E06000046,Isle_of_Wight,SE
```

station usage scenario data has the form

```
timestep,NLC_gb,day_usage
2015,375,204.4242424
2015,500,17129.24451
2015,501,30998.56593
...
```

So columns 1,2 and 7(8) of predicte rail demand give the scenario data for the predicted year

```bash
# Extracts daily and yearly station usage from output of rail model
# and append data to station usage scenario data
# usage: bash extract_predicted_rail_demand.sh year
year=$1
predicted_dmd_file=./data/transport/gb/output/$year/predictedDemand.csv
day_usage_file=./data/scenarios/rail_day_usage.csv
year_usage_file=./data/scenarios/rail_year_usage.csv
if ! [ -f "$day_usage_file" ]; then
  echo ERROR: Could not find $day_usage_file
fi
if ! [ -f "$year_usage_file" ]; then
  echo ERROR: Could not find $year_usage_file
fi
if ! [ -f "$predicted_dmd_file" ]; then
  echo ERROR: Could not find $predicted_dmd_file
fi
# First create backup for current station usage data
cp $day_usage_file ${day_usage_file}.bkp
cp $year_usage_file ${year_usage_file}.bkp
# Count nb of lines in predicted demand file
nbLines=$(wc -l $predicted_dmd_file | cut -d' ' -f1)
# Loop through lines excluding the first one
for line in $(tail -$(($nbLines-1)) $predicted_dmd_file); do
  echo $line | cut -d, -f1,2,8 >> $year_usage_file
  echo $line | cut -d, -f1,2,9 >> $day_usage_file
less $year_usage_file
less $day_usage_file
echo DONE. Backup station usage scenario data is available in
echo   - ${year_usage_file}.bkp
echo   - ${day_usage_file}.bkp
```


### 9.3 Automatise validation process


### 9.4 `extract_gb_scenarios` reads station<sub>usage</sub> for future years

Added fake data for years 2018, 2030, 2050

```
2015,300092,1065.42857
2015,500000,355.8236915
2015,500001,355.8236915
2018,375,0
2018,500,0
2018,501,0
2018,502,0
2018,503,0
...
...
2018,500001,0
2030,375,0
2030,500,0
2030,501,0
...
...
2030,500001,0
2050,375,0
2050,500,0
2050,501,0
...
...
```

### 9.5 No data for station usage in 2018

The rail station in Winslow is built in year 2018 for which no data is available in the
scenario data. Numbers are given in the `*.properties` intervention file provided in the rail
model data

- `data/transport/TR_data_full/full/data/interventions/winslowRailStation.properties`

I am just replaceing the fake 2018 station usage scenario data with the numbers for the correct
NLC. For instance:

```
# data/scenarios/rail_day_usage.csv
...
2018,300092,0
2018,500000,0
2018,500001,0
...
```

becomes same for yearly usage.
