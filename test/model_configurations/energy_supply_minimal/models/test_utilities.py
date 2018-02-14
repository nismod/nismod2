from utilities import write_heat_demand_data, parse_season_day_period
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

def test_write_heat_demand_data():

    
    year = 2000
    data_res = np.arange(10).reshape((2,5))
    data_com = np.arange(10).reshape((2,5))

    write_heat_demand_data(year, data_res, data_com)




