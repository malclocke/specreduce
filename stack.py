#! /usr/bin/env python

import pyfits
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Stack FITS files')
parser.add_argument('file', type=str, nargs='+')
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

data = []
for f in args.file:
  data.append(pyfits.getdata(f))

master = np.mean(data, axis=0)
pyfits.writeto(args.outfile, master.astype(np.uint8))
