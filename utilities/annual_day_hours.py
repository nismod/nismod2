"""Generate a CSV of interval definitions for the hours of a typical annual day

CSV format for interval definitions uses three columns: id, start, end

Start and end are defined as durations counting from the start of the year,
using [ISO8601 duration format](https://en.wikipedia.org/wiki/ISO_8601#Durations)

Here, a single day of 24 hours represents the whole year, so e.g. 'MIDNIGHT' maps
onto the time from 00:00-01:00 for each of the 365 days of the year.
"""
import csv

def main():
    hour_ids = [
        'MIDNIGHT',
        'ONEAM',
        'TWOAM',
        'THREEAM',
        'FOURAM',
        'FIVEAM',
        'SIXAM',
        'SEVENAM',
        'EIGHTAM',
        'NINEAM',
        'TENAM',
        'ELEVENAM',
        'NOON',
        'ONEPM',
        'TWOPM',
        'THREEPM',
        'FOURPM',
        'FIVEPM',
        'SIXPM',
        'SEVENPM',
        'EIGHTPM',
        'NINEPM',
        'TENPM',
        'ELEVENPM'
    ]

    with open('annual_day_hours.csv', 'w', newline='') as fh:
        w = csv.writer(fh)
        w.writerow(('id', 'start', 'end'))
        for day in range(365):
            for hour in range(24):
                from_ = 'P{}DT{}H'.format(day, hour)

                if (hour == 23):
                    to_ = 'P{}DT{}H'.format(day + 1, 0)
                else:
                    to_ = 'P{}DT{}H'.format(day, hour + 1)

                w.writerow((
                    hour_ids[hour],
                    from_,
                    to_
                ))

if __name__ == '__main__':
    main()
