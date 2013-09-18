#! /usr/bin/env python
import pyfits
import argparse
import numpy as np
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description='Find the pixel location of the zero order center')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', type=str, help='Output filename',
    required=True)
parser.add_argument('--spacing', type=float, required=True,
    help='Channel spacing (Angstrom / pixel')
parser.add_argument('--samplewidth', type=int, default=20,
    help='Width each side of zero order peak to sample.')
parser.add_argument('--maxx', type=int,
    help='Maximum X value for finding first order peak.')
parser.add_argument('--degree', type=int, default=7,
    help='Degree of polynomial fit')
parser.add_argument('--visualise', action='store_true',
    help='Visualise the zero order peak and fitted curve')

args = parser.parse_args()

f = pyfits.open(args.filename)
data = f[0].data.sum(axis=0)
s = data

if args.maxx:
  s = s[:args.maxx]

header = f[0].header

datamax = s.argmax()
left = datamax - args.samplewidth
right = datamax + args.samplewidth

if left < 0:
  left = 0

y = s[left:right]
x = np.arange(len(y))
z = np.polyfit(x, y, args.degree)
p = np.poly1d(z)
xp = np.linspace(0, len(y), 100)
maxpos = xp[p(xp).argmax()] + left

print '%s: Data peak: %d, polyfit peak: %f' % (args.filename, datamax, maxpos)

if args.visualise:
  plt.plot(x, y, '.', xp, p(xp), '-')
  plt.show()

header.update('CRVAL1', 0.0)
header.update('CRPIX1', float(maxpos))
header.update('CDELT1', args.spacing)
header.update('CUNIT1', 'Angstrom')
header.update('CTYPE1', 'Wavelength')
pyfits.writeto(args.outfile, data.astype('int32'), header, output_verify='fix')
