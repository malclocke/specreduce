#! /usr/bin/env python
import pyfits
import argparse
import spectraplot

parser = argparse.ArgumentParser(description='Find the pixel location of the zero order center')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--outfile', type=str, help='Output filename', required=True)
parser.add_argument('--spacing', type=float, required=True,
    help='Channel spacing (Angstrom / pixel')

args = parser.parse_args()

f = pyfits.open(args.filename)
s = f[0].data.sum(axis=0)
header = f[0].header

# FIXME - Fit a curve here and find maxima
maxpos = s.argmax()

header.update('CRVAL1', 0.0)
header.update('CRPIX1', float(maxpos))
header.update('CDELT1', args.spacing)
header.update('CUNIT1', 'Angstrom')
header.update('CTYPE1', 'Wavelength')

print s

pyfits.writeto(args.outfile, s.astype('int32'), header, output_verify='fix')
