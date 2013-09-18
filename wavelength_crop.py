#! /usr/bin/env python
import pyfits
import argparse
import specreduce
import numpy as np

parser = argparse.ArgumentParser(
    description='Crop spectra between specified wavelengths')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', type=str, help='Output filename',
    required=True)
parser.add_argument('--min', type=int, default=3800,
    help='Minimum angstrom value')
parser.add_argument('--max', type=int, default=8000,
    help='Maximum angstrom value')

args = parser.parse_args()

f = pyfits.open(args.filename)
header = f[0].header

spectra = specreduce.BessSpectra(f)
calibration = spectra.calibration
wl = np.array(spectra.wavelengths())
left = np.argmax(wl>args.min)
right = np.argmax(wl>args.max)

print '%s: Cropping %d to %d' % (args.filename, left, right)

cropped = spectra.data()[left:right]
header.update('CRVAL1', calibration.angstrom(left+1))
header.update('CRPIX1', 1.0)
header.update('CRPLFT', left, 'Left of crop area from wavelength_crop.py')
header.update('CRPRGT', right, 'Right of crop area from wavelength_crop.py')
pyfits.writeto(args.outfile, cropped, header, output_verify='fix')
