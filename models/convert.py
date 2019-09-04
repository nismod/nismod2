
"""Energy demand and supply adaptors
"""
from smif.convert import RegionAdaptor, IntervalAdaptor, UnitAdaptor


class ConvertGWMW(UnitAdaptor):
    """Convert GW to MW for energy demand-supply
    """


class ConvertLADtoEnergyHub(RegionAdaptor):
    """Convert LAD to Energy Hub for energy demand-supply
    """


class ConvertHourlyToSeasonalWeek(IntervalAdaptor):
    """Convert Hourly to Seasonal Week for energy demand-supply
    """


class ConvertLADtoPostcodeSector(RegionAdaptor):
    """Convert LAD to Postcode Sector for digital from scenarios
    """
