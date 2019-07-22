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
