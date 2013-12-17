#! /usr/bin/env python
import pyfits
import argparse
import dateutil.parser

parser = argparse.ArgumentParser(
    description='Show date with fractional day')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--keyword', '-k', type=str, default='DATE-OBS',
    help='FITS header keyword for date.  Default: DATE-OBS')

args = parser.parse_args()

f = pyfits.open(args.filename)

header = f[0].header
timestamp = dateutil.parser.parse(header[args.keyword])

month = timestamp.strftime('%b')

day = timestamp.day

seconds_expired_in_day = (timestamp.hour * 3600) + (timestamp.minute * 60) + timestamp.second
fraction_of_day = float(seconds_expired_in_day) / 86400
day_with_fraction = float(day) + fraction_of_day

print '%d %s %.3f' % (timestamp.year, month, day_with_fraction)
