#!/usr/bin/env python
import pyfits
import numpy as np
import argparse

parser = argparse.ArgumentParser(description='Automatically crop the binning area of a spectra')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--filterfactor', type=float, default=0.5,
    help='Factor for selecting the start of the crop area, based on the maximum binned value.')
parser.add_argument('--padding', type=int, default=10,
    help='Number of rows to pad either side of the binning area.')
parser.add_argument('--outfile', '-o', type=str, required=True)

args = parser.parse_args()

f = pyfits.open(args.filename)
d = f[0].data
header = f[0].header
s = d.sum(axis=1)

maxima = s.max()
filterfactor = args.filterfactor
top = np.argmax(s>maxima*filterfactor)
bottom = top + np.argmax(s[top:]<maxima*filterfactor)

print 'detected maxima: %d top: %d bottom: %d' % (maxima, top, bottom)

top = top - args.padding
bottom = bottom + args.padding

if top < 0:
  print 'WARN: Crop extends past top of image'
  top = 0

if bottom > d.shape[1]:
  print 'WARN: Crop extends past bottom of image'
  bottom = d.shape[1]

crop_height = bottom - top

print 'calculated crop %d rows (%d:%d) from %s' % (crop_height, top, bottom, args.filename)

if crop_height <= args.padding * 2:
  print 'ERR: %s has zero height area to crop' % (args.filename)
  exit(1)

cropped = d[top:bottom]
header.update('croptop', top, 'top of crop area in raw image')
header.update('cropbot', bottom, 'bottom of crop area in raw image')
header.update('cropfac', filterfactor, 'filterfactor for autocrop.py')
pyfits.writeto(args.outfile, cropped, header, output_verify='fix')
