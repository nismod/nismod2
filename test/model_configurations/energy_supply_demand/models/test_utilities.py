from energy_supply_toy import (parse_season_day_period,
                               write_load_shed_costs,
                               write_annual_rows_into_array,
                               write_timestep_rows_into_array,
                               compute_interval_id)
import numpy as np
import pytest

@pytest.mark.parametrize("test_input,expected", [
(1, (1,1,1)),
(24, (1,1,24)),
(25, (1,2,1)),
(238, (2,3,22)),
(239, (2,3,23)),
(240, (2,3,24)),
(241, (2,4,1)),
(242, (2,4,2)),
(243, (2,4,3)),
(384, (3,2,24)),
(385, (3,3,1)),
(670, (4,7,22)),
(671, (4,7,23)),
(672, (4,7,24))
])
def test_parse_season_day_period(test_input, expected):

    actual = parse_season_day_period(test_input)
    assert actual == expected

@pytest.mark.parametrize("test_input,expected", [
((1,1,1), 1),
((1,1,24), 24),
((1,2,1) , 25),
((2,3,22), 238),
((2,3,23), 239),
((2,3,24), 240),
((2,4,1), 241),
((2,4,2), 242),
((2,4,3), 243),
((3,2,24), 384),
((3,3,1), 385),
((4,7,22), 670),
((4,7,23), 671),
((4,7,24), 672),
])
def test_compute_interval_id(test_input, expected):
    season = test_input[0]
    day = test_input[1]
    period = test_input[2]
    actual = compute_interval_id(season, day, period)
    assert actual == expected

def test_write_load_shed_costs():

    elec = 2332345
    gas = 23234

    write_load_shed_costs(elec, gas)


def test_annual_row_to_array():

    rows = [('1', '1', 19840.0)]
    expected = np.array([[19840.0]])

    actual = write_annual_rows_into_array(rows)
    assert actual == expected


def test_timestep_row_to_array():

    rows = [(1, 1, 1, '1', 21131.0), (1, 1, 2, '2', 20919.0), 
            (1, 1, 3, '3', 19957.0), (1, 1, 4, '4', 19159.0)]
    expected = np.array([[21131.0, 0, 0, 0], 
                         [0, 20919.0, 0, 0], 
                         [0, 0, 19957.0, 0], 
                         [0, 0, 0, 19159.0]
                         ])

    actual = write_timestep_rows_into_array(rows)
    np.testing.assert_equal(actual, expected)
