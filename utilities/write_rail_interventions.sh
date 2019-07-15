# Convert base year rail demand csv file into intervention file
# usage: bash write_rail_interventions in out
inputFile=$1
outputInterventionFile=$2
if [ -f $inputFile ]; then
    rm -i $outputInterventionFile
fi
first_columns=name,type,technical_lifetime_value,techinal_lifetime_units,
echo $first_columns$(head -1 $inputFile) > $outputInterventionFile

nbLines=$(wc -l $inputFile | cut -d' ' -f1)
for line in $(tail -$(($nbLines-1)) $inputFile)
do
    name=new$(echo $line | cut -d, -f3)
    echo $name,NewRailStation,100,y,$line >> $outputInterventionFile
done
