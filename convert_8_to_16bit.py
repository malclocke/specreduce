#! /usr/bin/env python

import pyfits
import numpy as np
import argparse
import specreduce

parser = argparse.ArgumentParser(description='Convert 8 to 16 bit fits')
parser.add_argument('file', type=str)
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

hdulist = pyfits.open(args.file)
header = hdulist[0].header

data = hdulist[0].data.astype('uint16') * 256

pyfits.writeto(args.outfile, data, header, output_verify = 'fix')
