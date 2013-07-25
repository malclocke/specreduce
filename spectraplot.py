import pyfits
import matplotlib.pyplot as plt
import sys
import argparse

class PixelAngstromMapper:
  def __init__(self, zero_position, angstrom_per_pixel):
    self.zero_position = zero_position
    self.angstrom_per_pixel = angstrom_per_pixel

  def angstrom(self, pixel):
    return self.angstrom_per_pixel * (pixel + 1 - self.zero_position)

class ElementLine:
  def __init__(self, angstrom, label):
    self.angstrom = angstrom
    self.label = label

class Element:
  def __init__(self, name):
    self.name = name
    self.lines = []

  def add_line(self, angstrom, label):
    self.lines.append(ElementLine(angstrom, label))



parser = argparse.ArgumentParser(description='Process linear SA100 spectra')
parser.add_argument('filename', type=str, help='FITS filename')
parser.add_argument('--zero', dest='zero_position', type=int, default=0,
                    help='Pixel position of zero order image')
parser.add_argument('--calibration', dest='calibration', type=str,
                    help='Calibration pixel position.  Format pixel:angstrom')

args = parser.parse_args()

hdulist = pyfits.open(args.filename)
mean_data = hdulist[0].data.mean(axis=0)

calibration_position, calibration_angstrom = [int(i) for i in args.calibration.split(':')]

angstrom_per_pixel = float(calibration_angstrom) / (calibration_position - args.zero_position)

pam = PixelAngstromMapper(args.zero_position, angstrom_per_pixel)


wl = [pam.angstrom(i) for i in range(len(mean_data))]

plt.xlabel(r'Wavelength ($\AA$)')
plt.ylabel('Relative intensity')
plt.plot(wl, mean_data)

hydrogen = Element('Hydrogen')
hydrogen.add_line(6563, r'H$\alpha$')
hydrogen.add_line(4861, r'H$\beta$')
hydrogen.add_line(4341, r'H$\gamma$')

calcium = Element('Calcium')
calcium.add_line(3968, 'Ca H')
calcium.add_line(3934, 'Ca K')

for line in hydrogen.lines:
  plt.axvline(x=line.angstrom)
  plt.text(line.angstrom, 10, line.label)

for line in calcium.lines:
  plt.axvline(x=line.angstrom)
  plt.text(line.angstrom, 10, line.label)

plt.show()
