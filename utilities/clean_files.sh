# Clean newlines for all files (from windows to unix)
# - run from inside vagrant vm
# - might need to clean this first!  
#     tr -d '\r' < utilities/clean_files.sh > /tmp/clean_files.sh 
#     mv /tmp/clean_files.sh utilities/clean_files.sh

shopt -s nullglob
to_clean=(./provision/*)
shopt -u nullglob

for filename in ${to_clean[@]}; do
    bname=$(basename $filename)
    tr -d '\r' < $filename > /tmp/$bname
    mv /tmp/$bname $filename
done;
