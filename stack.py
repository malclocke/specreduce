#! /usr/bin/env python

import pyfits
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Stack FITS files')
parser.add_argument('file', type=str, nargs='+')
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

exptime = 0.0
header = False

data = []
for f in args.file:
  hdulist = pyfits.open(f)
  if header == False:
    header = hdulist[0].header
  if 'EXPTIME' in hdulist[0].header:
    exptime += float(hdulist[0].header['EXPTIME'])
  data.append(hdulist[0].data)

if exptime > 0.0:
  header.update('EXPTIME', exptime)

master = np.mean(data, axis=0)

print 'Stacked %d frames' % (len(data))

pyfits.writeto(args.outfile, master.astype(np.uint8), header)
