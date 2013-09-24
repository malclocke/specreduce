#! /usr/bin/env python
import pyfits
import argparse

parser = argparse.ArgumentParser(
    description='Bin a 2D spectra to 1D')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', type=str, help='Output filename',
    required=True)

args = parser.parse_args()

f = pyfits.open(args.filename)
header = f[0].header
data = f[0].data.sum(axis=0)

pyfits.writeto(args.outfile, data.astype('int32'), header, output_verify='fix')
