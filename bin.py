#! /usr/bin/env python
import pyfits
import argparse
import numpy as np

parser = argparse.ArgumentParser(
    description='Bin a 2D spectra to 1D')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', '-o', type=str, help='Output filename',
    required=True)
parser.add_argument('--skywidth', '-s', type=int, default=6,
    help='Width of area for sky subtraction')

args = parser.parse_args()

f = pyfits.open(args.filename)
header = f[0].header
data = f[0].data.sum(axis=0)
print data

sky = np.mean(f[0].data[0:args.skywidth], axis = 0)
sky *= (len(f[0].data) / args.skywidth)
data -= sky

pyfits.writeto(args.outfile, data.astype('int32'), header, output_verify='fix')
