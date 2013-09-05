#! /usr/bin/env python
import pyfits
import argparse
import spectraplot
import numpy as np

parser = argparse.ArgumentParser(
    description='Normalise spectra.')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', type=str, help='Output filename',
    required=True)

args = parser.parse_args()

f = pyfits.open(args.filename)
header = f[0].header
data = f[0].data.astype('float')

factor = data.max()
data = data / factor

print '%s: Normalising with factor %f' % (args.filename, factor)

pyfits.writeto(args.outfile, data, header, output_verify='fix')
