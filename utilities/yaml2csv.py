"""Convert list-of-dict style yaml to CSV format

Usage:

    python yaml2csv.py ./path/to/file.yml ./path/to/output.csv

    python yaml2csv.py ./path/to/file.yml ./path/to/output.csv "list,of,keys,to,use,as,header"

"""
import csv
import sys

from ruamel.yaml import YAML


def main(input_file, output_file, keys=None):
    """Read YAML file, write CSV to STDOUT
    """
    yaml = YAML()
    with open(input_file, 'r') as file_handle:
        data = yaml.load(file_handle)

    if keys is None:
        keys = guess_keys(data)
    else:
        keys = keys.split(",")

    with open(output_file, 'w', newline='') as file_handle:
        writer = csv.DictWriter(file_handle, fieldnames=keys, extrasaction='ignore',lineterminator='\n')
        writer.writeheader()

        for item in data:
            writer.writerow(item)


def guess_keys(data):
    """Guess keys should be uniform from first item
    """
    return list(data[0].keys())

if __name__ == '__main__':
    if len(sys.argv) == 3:
        main(sys.argv[1], sys.argv[2])
        exit()

    if len(sys.argv) == 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
        exit()

    print("""\
Convert list-of-dict style yaml to CSV format

Usage:

    python yaml2csv.py ./path/to/file.yml ./path/to/output.csv

    python yaml2csv.py ./path/to/file.yml ./path/to/output.csv "list,of,keys,to,use,as,header"
""")
