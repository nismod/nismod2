"""Translate from .properties files to smif CSVs of interventions
"""
import collections
import configparser
import csv
import glob
import os
import sys


def main(input_dir, output_dir):
    # look for .properties files in input_dir and any child directories
    filenames = glob.glob(os.path.join(input_dir, '*.properties'))
    filenames.extend(glob.glob(os.path.join(input_dir, '**', '*.properties')))
    print("Found {} interventions.properties files in {}".format(len(filenames), input_dir))

    interventions = collections.defaultdict(list)
    for filename in filenames:
        with open(filename) as file_handle:
            # Java .properties files are almost equivalent to .ini files
            # - add a section header
            # - then we can use configparser to read
            parser = configparser.ConfigParser()
            conf_str = '[root]\n' + file_handle.read()
            parser.read_string(conf_str)
            config = dict(parser['root'])
            # use the file name as the smif name (unique id)
            config['name'] = str(os.path.basename(filename)).replace('.properties', '')
            # append to list by type - different types have different keys, so will write to
            # separate CSVs
            interventions[config['type']].append(config)

    for type_, list_ in interventions.items():
        # write to CSV in output_dir
        output_filename = "{}.csv".format(type_)
        output_file = os.path.join(output_dir, output_filename)
        print("Writing {} interventions to {}".format(len(list_), output_file))

        with open(output_file, 'w', newline='') as file_handle:
            writer = csv.DictWriter(file_handle, fieldnames=list_[0].keys())
            writer.writeheader()
            for int_ in list_:
                writer.writerow(int_)

if __name__ == '__main__':
    INPUT_DIR = None
    OUTPUT_DIR = None

    try:
        INPUT_DIR = sys.argv[1]
        OUTPUT_DIR = sys.argv[2]
    except IndexError:
        print('Usage: python {} <path/to/interventions> <path/to/output>'.format(__file__))

    if INPUT_DIR is not None and OUTPUT_DIR is not None:
        main(INPUT_DIR, OUTPUT_DIR)
