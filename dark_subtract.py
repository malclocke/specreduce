#! /usr/bin/env python

import pyfits
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Dark subtract FITS file')
parser.add_argument('dark', type=str)
parser.add_argument('file', type=str)
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

f = pyfits.open(args.file)
data = f[0].data.astype('int16')
header = f[0].header

if args.dark:
  dark = pyfits.getdata(args.dark).astype('int16')
  subtracted = np.subtract(data, dark)
  # Replace all negative values with 0
  subtracted = subtracted.clip(0, 255)

pyfits.writeto(
  args.outfile, subtracted.astype(np.uint8), header, output_verify='fix'
)
