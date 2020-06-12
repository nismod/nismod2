"""List all files in data directory
"""
import csv
import os
import re

from glob import glob

# Change to nismod root directory (one up from script utilities directory)
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

with open("data_files.csv", 'w') as fh:
    writer = csv.writer(fh)
    writer.writerow(('model', 'filename'))

    files = glob('data/**/*.*', recursive=True)
    writer.writerows(
        (re.search("data/([^/]*)", filename)[1], filename)
        for filename in sorted(files)
    )
