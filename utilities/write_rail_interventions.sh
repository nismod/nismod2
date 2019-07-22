# Convert base year rail demand csv file into intervention file
# usage: bash write_rail_interventions in out
inputFile=$1
outputInterventionFile=$2
if [ -f $inputFile ]; then
    rm -i $outputInterventionFile
fi
first_columns=NLC_gb,name,type,technical_lifetime_value,technical_lifetime_units,
echo $first_columns$(head -1 $inputFile | cut -d, -f2-6,9-12) > $outputInterventionFile

nbLines=$(wc -l $inputFile | cut -d' ' -f1)
for line in $(tail -$(($nbLines-1)) $inputFile)
do
    # Several interventions can have the same name, but different MODE (TUBE, NRAIL..)
    # disambiguating by adding the mode name to the intervention name
    mode=$(echo $line | cut -d, -f2)
    name=new$(echo $line | cut -d, -f3)_$mode
    NLCvalue=$(echo $line | cut -d, -f1)
    echo $NLCvalue,${name},NewRailStation,100,y,$(echo $line | cut -d, -f2-6,9-12) >> $outputInterventionFile
done
