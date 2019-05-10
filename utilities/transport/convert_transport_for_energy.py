"""Read transport outputs (electric vehicle trips and energy consumption) and output formatted
as smif scenarios
"""
import os
import sys
from glob import glob

import pandas as pd

def main(input_dirname, scenario_suffix, output_dirname):
    """Run script
    """
    trip_csvs = glob(os.path.join(input_dirname, '**/zonalTemporalEVTripStarts.csv'))
    trips = pd.concat(
        read_csv(filename, 'electric_vehicle_trip_starts')
        for filename in trip_csvs
    )
    print("Found trip_starts for {}".format(trips.timestep.unique()))
    trips.to_csv(
        os.path.join(
            output_dirname,
            'electric_vehicle_trip_starts__{}.csv'.format(scenario_suffix)
        ),
        index=False
    )

    elec_csvs = glob(os.path.join(input_dirname, '**/zonalTemporalEVTripElectricity.csv'))
    elec = pd.concat(
        read_csv(filename, 'electric_vehicle_electricity_consumption')
        for filename in elec_csvs
    )
    print("Found electricity_consumption for {}".format(elec.timestep.unique()))
    elec.to_csv(
        os.path.join(
            output_dirname,
            'electric_vehicle_electricity_consumption__{}.csv'.format(scenario_suffix)
        ),
        index=False
    )


def read_csv(filename, varname):
    """Read, melt, check year, rename
    """
    df_in = pd.read_csv(filename)
    # df_in.head()
    #    year       zone  MIDNIGHT  ONEAM  TWOAM  ...  EIGHTPM  NINEPM  TENPM  ELEVENPM
    # 0  2015  E08000030     12.95    0.0    0.0  ...     3.37    1.90   3.02       0.0
    # 1  2015  E09000003     18.04    0.0    0.0  ...    12.84   10.38  13.81       0.0
    # 2  2015  E09000002      0.00    0.0    0.0  ...     3.72    2.56   2.79       0.0
    # 3  2015  E08000031      0.00    0.0    0.0  ...     4.06    9.06   5.92       0.0
    # 4  2015  E07000180      0.00    0.0    0.0  ...     0.79    0.00   0.00       0.0

    df_out = df_in.melt(
        id_vars=['year', 'zone']
    ).rename(
        columns={
            'year': 'timestep',
            'zone': 'lad_gb_2016',
            'variable': 'annual_day_hours',
            'value': varname
    })
    # df_out.head()
    #    timestep lad_gb_2016 annual_day_hours  electric_vehicle_electricity_consumption
    # 0      2015   E08000030         MIDNIGHT                                     12.95
    # 1      2015   E09000003         MIDNIGHT                                     18.04
    # 2      2015   E09000002         MIDNIGHT                                      0.00
    # 3      2015   E08000031         MIDNIGHT                                      0.00
    # 4      2015   E07000180         MIDNIGHT                                      0.00

    return df_out

if __name__ == '__main__':
    try:
        INPUT_DIRNAME = sys.argv[1]
        SUFFIX = sys.argv[2]
        OUTPUT_DIRNAME = sys.argv[3]
    except IndexError:
        print('Usage: python {} <input dirname> <scenario> <output dirname>'.format(__file__))
        exit(-1)

    main(INPUT_DIRNAME, SUFFIX, OUTPUT_DIRNAME)
