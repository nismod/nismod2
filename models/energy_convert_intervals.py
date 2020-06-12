"""Sample 4 weeks of 24*7 hours of energy demand from the 24*365 simulated.
"""
import pandas

from datetime import datetime, timedelta
from smif.data_layer import DataArray
from smif.exception import SmifException
from smif.model import SectorModel

class SampleEnergyIntervals(SectorModel):
    """Adaptor to sample from energy demand
    """
    def simulate(self, data_handle):
        """Read inputs, determine sample, sample, write out.
        """
        # read all inputs
        ed_all = pandas.concat(
            (data_handle.get_data(input_).as_df() for input_ in self.inputs),
            axis=1) \
            .reset_index()

        # determine sample
        intervals = self.calculate_intervals(data_handle.current_timestep, ed_all)

        # sample
        ed_sampled = ed_all[ed_all.hourly.isin(intervals)].copy()

        # relabel for output dims
        # one-based hour index for seasonal weeks
        hour_to_sw = {hour: i + 1 for i, hour in enumerate(intervals)}
        ed_sampled['seasonal_week'] = ed_sampled.hourly.apply(lambda h: hour_to_sw[h])
        ed_sampled = ed_sampled \
            .drop(columns=['hourly']) \
            .set_index(['energy_hub', 'seasonal_week'])

        # write all outputs
        for output, spec in self.outputs.items():
            df = ed_sampled[[output]]
            da = DataArray.from_df(spec, df)
            data_handle.set_results(output, da.data)

    @staticmethod
    def calculate_intervals(current_timestep, ed_all):
        # aggregate to national demand (ignore regional variation)
        ed_national = ed_all \
            .drop(columns=['energy_hub']) \
            .groupby('hourly') \
            .sum() \
            .reset_index()

        # add actual dates so we can use weekly resampling
        ed_national['date'] = ed_national.hourly.apply(
            lambda h: datetime(current_timestep, 1, 1) + timedelta(hours=h-1))

        ed_national = ed_national \
            .drop(columns=['hourly']) \
            .set_index('date')

        # find total demand per hour (important that all columns are energy demand values at
        # this point)
        ed_national['energy_demand'] = ed_national.sum(axis=1)

        # find max hour for each week - we're going to pick the weeks with representative peaks
        weekly_peaks = ed_national.resample('w').max()

        # trim final partial week - can't think of a neater way to guarantee that all samples
        # will always fit within the year. Not trying to align on Monday starts either.
        weekly_peaks = weekly_peaks[:-1]

        # NOTE - this is a key part of the sampling method, could pick other quantiles
        # pick min, terciles, max - interpolate to nearest so that we can sample these rows
        quantiles = weekly_peaks[['energy_demand']] \
            .quantile([0, 1/3, 2/3, 1], interpolation='nearest')

        # find dates of quantiles
        # - drop duplicates in case of any static demand
        midweeks = weekly_peaks[weekly_peaks.energy_demand.isin(quantiles.energy_demand)] \
            .drop_duplicates(subset='energy_demand') \
            .reset_index() \
            .date

        # date of the start of the week
        starts = [date - timedelta(days=3) for date in midweeks]

        # timedelta from start of the year
        year_start = datetime(current_timestep, 1, 1)
        deltas = [start - year_start for start in starts]

        # back to one-based hourly intervals
        hours = [delta.days * 24 + 1  for delta in deltas]

        intervals = []
        for hour in hours:
            intervals.extend(range(hour, hour + 24 * 7))

        msg = "Unexpected number of intervals, got {}, expected 672 (24 * 7 * 4)"
        assert len(intervals) == 24 * 7 * 4, msg.format(len(intervals))

        return intervals
