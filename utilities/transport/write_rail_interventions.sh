# Convert base year rail demand csv file into intervention file
# usage: bash write_rail_interventions in out
# -------------
# Note that the base year rail usage file only contains stations that are older
# than the base year.
# Future stations must therefore be added to the file that this script generates.
# Up to now this must be done by hand.

########
# TODO #
########
# Provide the script with a list of potential future stations
# The script reads the corresponding .properties files and appends the content
# to the previously generated intervention data.

inputFile=$1
outputInterventionFile=$2
if [ -f $inputFile ]; then
    rm -f $outputInterventionFile
fi

columns=NLC,name,type,technical_lifetime_value,technical_lifetime_units,mode,station,naPTANname,easting,northing,runDays,LADcode,LADname,area
echo $columns > $outputInterventionFile

nbLines=$(wc -l $inputFile | cut -d' ' -f1)
for line in $(tail -$(($nbLines-1)) $inputFile)
do
    # Several interventions can have the same name, but different MODE (TUBE, NRAIL..)
    # disambiguating by adding the mode name to the intervention name
    mode=$(echo $line | cut -d, -f2)
    name=new$(echo $line | cut -d, -f3)_$mode
    NLCvalue=$(echo $line | cut -d, -f1)
    baseYearData=$(echo $line | cut -d, -f2-6,9-12)
    echo $NLCvalue,${name},NewRailStation,100,y,$baseYearData >> $outputInterventionFile
done
echo Intervention data written in $outputInterventionFile
echo Be sure to add potential future stations to the intervention data file.
