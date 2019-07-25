"""Read from transport data to output smif scenario
"""
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
            'variable': 'lad_gb_2016',
            'value': 'car_zonal_journey_costs',
        }
    )

    df_out.to_csv(output_filename, index=False)

if __name__ == '__main__':
    INPUT_FILENAME = '../data/transport/TR_data_full/full/data/csvfiles/carZonalJourneyCosts.csv'
    OUTPUT_FILENAME = '../data/scenarios/rail_car_zonal_journey_costs.csv'

    try:
        INPUT_FILENAME = sys.argv[1]
        OUTPUT_FILENAME = sys.argv[2]
    except IndexError:
        print('Usage: python {} <input filename> <output filename>'.format(__file__))

    print('Using input: {}'.format(INPUT_FILENAME))
    print('Using output: {}'.format(OUTPUT_FILENAME))

    main(INPUT_FILENAME, OUTPUT_FILENAME)
