"""Read from transport data to output smif scenario
"""
import os
import sys

import pandas as pd


def main(input_filename, output_filename):
    """Run script
    """
    # Could use glob to find similarly-named engineTypeFraction*.csv
    df_in = pd.read_csv(input_filename)

    # Melt to tidy format
    df_out = df_in.melt(
        id_vars=['year']
    ).rename(
        columns={
            'year': 'timestep',
            'variable': 'NLC_gb',
            'value': 'rail_journey_times',
        }
    )

    df_out.to_csv(output_filename, index=False)

if __name__ == '__main__':
    BASE_PATH = os.path.join(os.path.dirname(__file__), '..', '..')
    INPUT_FILENAME = os.path.join(
        BASE_PATH, 'data/transport/gb/data/csvfiles/railStationGeneralisedJourneyTimes.csv')
    OUTPUT_FILENAME = os.path.join(
        BASE_PATH, 'data/scenarios/rail_station_journey_times.csv')

    try:
        INPUT_FILENAME = sys.argv[1]
        OUTPUT_FILENAME = sys.argv[2]
    except IndexError:
        print('Usage: python {} <input filename> <output filename>'.format(__file__))

    print('Using input: {}'.format(INPUT_FILENAME))
    print('Using output: {}'.format(OUTPUT_FILENAME))

    main(INPUT_FILENAME, OUTPUT_FILENAME)
