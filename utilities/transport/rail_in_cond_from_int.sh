# Generate initial conditions file from list of interventions.
# Usage : bash rail_in_cond_from_int.sh
# Input: interventions file

# NLC_gb,name,type,..,LADcode,LADname,Area
# 375,newEnerglyn_&_Churchill_Park_NRAIL,NewRailStation,...,W06000018,Caerphilly,OTHER
# 500,newActon_Town_TUBE,NewRailStation,...,E09000009,Ealing,LT
# ...

# to

# name, build_year
# newEnerglyn_&_Churchill_Park_NRAIL, 1975
# newActon_Town_TUBE, 1975
# ...

path_interventions=../../data/interventions/transport_rail.csv
path_initial_conditions=../../data/initial_conditions/base_year_railstations.csv
if [ -f "$path_initial_conditions" ] ; then
    rm -i $path_initial_conditions
fi

build_year=1975
for line in $(cat $path_interventions)
do
    echo $(echo $line | cut -d, -f2),$build_year >> $path_initial_conditions
done

# Update first line
sed -i "1s/1975/build_year/" $path_initial_conditions
