"""Read from transport data to output smif scenario
"""
import sys

import pandas as pd


def main(input_filename, output_filename):
    """Run script
    """
    # Could use glob to find similarly-named engineTypeFraction*.csv
    df_in = pd.read_csv(input_filename)

    # df_in.head()
    #    year vehicle  ICE_PETROL  ICE_DIESEL  ...  PHEV_PETROL  PHEV_DIESEL       BEV
    # 0  2015     CAR    0.612000    0.377800  ...     0.000500     0.000308  0.000813
    # 1  2016     CAR    0.594514    0.367006  ...     0.013749     0.008465  0.003647
    # 2  2017     CAR    0.577029    0.356211  ...     0.026997     0.016622  0.006481
    # 3  2018     CAR    0.559543    0.345417  ...     0.040246     0.024779  0.009315
    # 4  2019     CAR    0.542057    0.334623  ...     0.053494     0.032936  0.012149

    # Melt to tidy format
    df_out = df_in.melt(
        id_vars=['year']
    ).rename(
        columns={
            'year': 'timestep',
            'variable': 'NLC_gb',
            'value': 'rail_journey_fares',
        }
    )

    # df_out.head()
    #    timestep vehicle engine_type  engine_type_fractions
    # 0      2015     CAR  ICE_PETROL               0.612000
    # 1      2016     CAR  ICE_PETROL               0.594514
    # 2      2017     CAR  ICE_PETROL               0.577029
    # 3      2018     CAR  ICE_PETROL               0.559543
    # 4      2019     CAR  ICE_PETROL               0.542057

    df_out.to_csv(output_filename, index=False)

if __name__ == '__main__':
    INPUT_FILENAME = '../data/transport/TR_data_full/full/data/csvfiles/railStationJourneyFares.csv'
    OUTPUT_FILENAME = '../data/scenarios/rail_station_journey_fares.csv'

    try:
        INPUT_FILENAME = sys.argv[1]
        OUTPUT_FILENAME = sys.argv[2]
    except IndexError:
        print('Usage: python {} <input filename> <output filename>'.format(__file__))

    print('Using input: {}'.format(INPUT_FILENAME))
    print('Using output: {}'.format(OUTPUT_FILENAME))

    main(INPUT_FILENAME, OUTPUT_FILENAME)
