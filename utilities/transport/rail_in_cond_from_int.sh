# Generate initial conditions file from base year rail usage file
# Usage : bash rail_in_cond_from_int.sh
# Input: base year rail usage file

# NLC,Mode,Station,...,LADcode,LADname,Area
# 375,NRAIL,Energlyn_&_Churchill_Park,..,W06000018,Caerphilly,OTHER
# 500,TUBE,Acton_Town,Acton_Town_Underground_Station,...,E09000009,Ealing,LT
# ...

# to

# name, build_year
# newEnerglyn_&_Churchill_Park_NRAIL, 1975
# newActon_Town_TUBE, 1975
# ...

path_baseYearRailUsage=../../data/transport/gb/data/csvfiles/baseYearRailUsage.csv
path_initial_conditions=../../data/initial_conditions/base_year_railstations.csv
if [ -f "$path_initial_conditions" ] ; then
    rm -i $path_initial_conditions
fi
if ! [ -f "$path_baseYearRailUsage" ] ; then
    echo ERROR: Could not find base year rail usage file $path_baseYearRailUsage
    exit 1
fi
echo Reading $path_baseYearRailUsage
build_year=1975
for line in $(cat $path_baseYearRailUsage)
do
    mode=$(echo $line | cut -d, -f2)
    intervention_name=new$(echo $line | cut -d, -f3)_$mode
    echo $intervention_name,$build_year >> $path_initial_conditions
done

# Update first line
sed -i "1s/.*/name,build_year/" $path_initial_conditions
