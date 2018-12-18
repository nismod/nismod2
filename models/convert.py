
"""Energy demand and supply adaptors
"""
from smif.convert import RegionAdaptor, IntervalAdaptor, UnitAdaptor


class ConvertGWMW(UnitAdaptor):

    pass


class ConvertLADtoEnergyHub(RegionAdaptor):

    pass


class ConvertHourlyToSeasonalWeek(IntervalAdaptor):

    pass
