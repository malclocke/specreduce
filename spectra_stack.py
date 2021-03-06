#! /usr/bin/env python

import pyfits
import numpy as np
import argparse
import specreduce

parser = argparse.ArgumentParser(description='Stack spectra files')
parser.add_argument('master', type=str)
parser.add_argument('file', type=str, nargs='+')
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

data = []
master = specreduce.BessSpectra(pyfits.open(args.master))
header = master.hdulist[0].header

if 'EXPTIME' in header:
  exptime = float(header['EXPTIME'])
else:
  exptime = 0.0

data.append(master.data())

crvals = []

for f in args.file:
  s = specreduce.BessSpectra(pyfits.open(f))
  data.append(s.interpolate_to(master))
  if 'EXPTIME' in s.header():
    exptime += float(s.header()['EXPTIME'])

dtype = master.hdulist[0].data.dtype.name
mean_crval = np.mean(crvals)

print 'Stacked %d frames' % (len(data))

stacked = np.mean(data, axis=0)
header.update('NBADD', len(data), 'Number of coadded frames')
header.update('EXPTIME', exptime)
pyfits.writeto(args.outfile, stacked.astype(dtype), header)
