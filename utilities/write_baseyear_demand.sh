# Extract base year tail demand from baseYearUsage.csv provided by rail model
inputFile=$1
outputFile=$2
if [ -f $outputFile ]; then
    rm -i $outputFile
fi

echo NLC,YearUsage,DayUsage > $outputFile
nbLines=$(wc -l $inputFile | cut -d' ' -f1)
for line in $(tail -$(($nbLines-1)) $inputFile)
do
    echo $line | cut -d, -f1,7,8 >> $outputFile
done
