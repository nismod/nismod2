"""Filter scenario data by timestep
"""
import glob
import os
import sys

import pandas

def main(input_dir, output_dir, timesteps):
    files = glob.glob(os.path.join(input_dir, '*.csv'))
    for fname in files:
        df = pandas.read_csv(fname)
        df = df[df.timestep.isin(timesteps)]
        df.to_csv(os.path.join(output_dir, os.path.basename(fname)), index=False)


if __name__ == '__main__':
    try:
        input_dir = sys.argv[1]
        output_dir = sys.argv[2]
        timesteps = [int(n) for n in sys.argv[3:]]
    except IndexError:
        sys.exit("Usage: python {} input_dir output_dir 2010 2020 2030...".format(__file__))

    print("From ", input_dir)
    print("To   ", output_dir)
    print("Steps", timesteps)
    main(input_dir, output_dir, timesteps)
