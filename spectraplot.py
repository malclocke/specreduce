#! /usr/bin/env python
import pyfits
import numpy as np
import matplotlib.pyplot as plt
import scipy.interpolate
import argparse
import os


class CalibrationReference:
  def __init__(self, pixel, angstrom):
    self.pixel = pixel
    self.angstrom = angstrom

class DoublePointCalibration:
  def __init__(self, reference1, reference2):
    self.reference1 = reference1
    self.reference2 = reference2

  def __repr__(self):
    return "<Calibration angstrom_per_pixel: %f>" % (
        self.angstrom_per_pixel()
    )

  def angstrom(self, pixel):
    return (self.slope() * (pixel - self.reference1.pixel)) + self.reference1.angstrom

  def slope(self):
    return self.angstrom_difference() / self.pixel_difference()

  def angstrom_difference(self):
    return self.reference1.angstrom - self.reference2.angstrom

  def pixel_difference(self):
    return self.reference1.pixel - self.reference2.pixel

  def angstrom_per_pixel(self):
    return self.slope()


class SinglePointCalibration:
  def __init__(self, reference, angstrom_per_pixel):
    self.reference = reference
    self._angstrom_per_pixel = angstrom_per_pixel

  def angstrom(self, pixel):
    return (self.angstrom_per_pixel() * (pixel - self.reference.pixel)) + self.reference.angstrom

  def angstrom_per_pixel(self):
    return self._angstrom_per_pixel


class ElementLine:
  def __init__(self, angstrom, label):
    self.angstrom = angstrom
    self.label = label

  def __repr__(self):
    return "%f (%s)" % (self.angstrom, self.label)

  def color(self):
    return 'red'

  def plot_label(self):
    return '%s (%.02f $\AA$)' % (self.label, self.angstrom)

  def plot_onto(self, axes):
    axes.axvline(x=self.angstrom, color=self.color())
    axes.text(self.angstrom, 10, self.plot_label(),
        rotation='vertical', verticalalignment='bottom')


class Plotable:
  def plot_onto(self, axes):
    axes.plot(self.wavelengths(), self.data(), label=self.label)

  def max(self):
    return self.data().max()

  def divide_by(self, other_spectra):
    divided = np.divide(self.data(), other_spectra.interpolate_to(self))
    divided[divided==np.inf]=0
    return divided

  def interpolate_to(self, spectra):
    return np.interp(spectra.wavelengths(), self.wavelengths(), self.data())


class Reference(Plotable):

  base_path = os.path.dirname(os.path.realpath(__file__))
  subdir = "references/"
  scale_factor = 1

  def __init__(self, reference, interpolate_source=False):
    self.hdulist = pyfits.open(self.reference_path(reference))
    self.label = 'Reference (%s)' % reference
    self.interpolate_source = interpolate_source

  def wavelengths(self):
    return self.hdulist[1].data.field(0)

  def scale_to(self, spectra):
    self.scale_factor = spectra.max() / self.data().max()
    return self.scale_factor

  def reference_path(self, reference):
    return os.path.join(self.reference_dir(), reference + '.fits')

  def reference_dir(self):
    return os.path.join(self.base_path, self.subdir)

  def data(self):
    return self.scale_factor * self.hdulist[1].data.field(1)


class ImageSpectra(Plotable):

  label = 'Raw data'
  calibration = False

  def __init__(self, data):
    self.raw = data

  def data(self):
    return self.raw.sum(axis=0)

  def set_calibration(self, calibration):
    self.calibration = calibration

  def wavelengths(self):
    if self.calibration:
      return [self.calibration.angstrom(i) for i in range(len(self.data()))]
    else:
      return range(len(self.data()))

  def plot_image_onto(self, axes):
    imgplot = axes.imshow(self.raw)
    imgplot.set_cmap('gray')

class BessSpectra(Plotable):

  label = 'Raw spectra'

  def __init__(self, hdulist):
    self.hdulist = hdulist
    self.calibration = SinglePointCalibration(
      CalibrationReference(self.get_header('CRPIX1'), self.get_header('CRVAL1')),
      self.get_header('CDELT1')
    )

  def plot_image_onto(self, axes):
    return False

  def get_header(self, header):
    return self.hdulist[0].header[header]

  def wavelengths(self):
    return [self.calibration.angstrom(i) for i in range(len(self.data()))]

  def data(self):
    return self.hdulist[0].data

class CorrectedSpectra(Plotable):

  smoothing = 20
  spacing   = 500
  k         = 1
  label     = 'Corrected'

  def __init__(self, uncorrected, reference):
    self.uncorrected = uncorrected
    self.reference = reference

  def wavelengths(self):
    return self.uncorrected.wavelengths()

  def divided(self):
    return self.uncorrected.divide_by(self.reference)

  def data(self):
    return np.divide(self.uncorrected.data(), self.smoothed())

  def smoothed(self):
    tck = scipy.interpolate.splrep(
      self.wavelengths(), self.divided(), s=self.smoothing, k=self.k
    )
    return scipy.interpolate.splev(self.wavelengths(), tck)


class FitsExport:
  def __init__(self, spectra):
    self.spectra = spectra

  def writeto(self, filename):
    export_hdu = pyfits.PrimaryHDU(self.spectra.data())
    export_hdu.scale('float32')
    export_header = export_hdu.header
    export_header.update('CRVAL1', self.spectra.wavelengths()[0])
    export_header.update('CRPIX1', 1.0)
    export_header.update('CDELT1', self.spectra.calibration.angstrom_per_pixel())
    export_header.update('CUNIT1', 'Angstrom')
    export_header.update('CTYPE1', 'Wavelength')
    print export_header
    export_hdu.writeto(filename)


def main():
  element_lines = {
    'Ha': ElementLine(6563, r'H$\alpha$'),
    'Hb': ElementLine(4861, r'H$\beta$'),
    'Hg': ElementLine(4341, r'H$\gamma$'),
    'Hd': ElementLine(4102, r'H$\delta$'),
    'CaH': ElementLine(3968, 'Ca H'),
    'CaK': ElementLine(3934, 'Ca K'),
  }

  parser = argparse.ArgumentParser(description='Process linear SA100 spectra')
  parser.add_argument('filename', type=str, help='FITS filename')
  parser.add_argument('--calibrate', '-c', dest='calibration', type=str,
      help='Calibration pixel position.  Format pixel:angstrom,pixel:angstrom or pixel,angstrom,angstrom_per_pixel')
  parser.add_argument('--lines', '-l', dest='lines', type=str,
                      help='Plot specified lines.')
  parser.add_argument('--title', '-t', dest='title', type=str, help='Plot title')
  parser.add_argument('--suptitle', '-s', dest='suptitle', type=str, help='Plot super-title, appears above title')
  parser.add_argument('--listlines', '-L', action='store_true',
      help='List available lines')
  parser.add_argument('--reference', '-r', dest='reference', type=str,
      help='Plot a reference spectra')
  parser.add_argument('--crop', '-C', action='store_true', help='Crop spectra')
  parser.add_argument('--croprange', type=str, default='3900:7000',
      help='Set crop range (default: 3900:7000)')
  parser.add_argument('--export', '-x', type=str,
      help='Export calibrated spectra to specified file in BeSS format')

  args = parser.parse_args()

  if args.listlines:
    for k, v in element_lines.iteritems():
      print "%4s %s" % (k, v)
    exit()

  hdulist = pyfits.open(args.filename)
  print hdulist.info()

  if hdulist[0].header['NAXIS'] == 1:
    base_spectra = BessSpectra(hdulist)
  else:
    base_spectra = ImageSpectra(hdulist[0].data)

  graph_subplot = plt.subplot(211)
  graph_subplot.set_ylabel('Relative intensity')

  if args.crop:
    crop_left, crop_right = args.croprange.split(':')
    graph_subplot.set_xlim(left=int(crop_left),right=int(crop_right))

  image_subplot = plt.subplot(212)
  image_subplot.set_xlabel('x px')
  image_subplot.set_ylabel('y px')
  base_spectra.plot_image_onto(image_subplot)

  plots = []
  plots.append(base_spectra)

  if args.calibration:
    calibration_elements = args.calibration.split(',')
    if len(calibration_elements) == 2:
      reference_1, reference_2 = calibration_elements
      pixel1, angstrom1 = reference_1.split(':')
      pixel2, angstrom2 = reference_2.split(':')

      if angstrom1 in element_lines:
        angstrom1 = element_lines[angstrom1].angstrom
      if angstrom2 in element_lines:
        angstrom2 = element_lines[angstrom2].angstrom

      calibration = DoublePointCalibration(
        CalibrationReference(int(pixel1), float(angstrom1)),
        CalibrationReference(int(pixel2), float(angstrom2))
      )
    elif len(calibration_elements) == 3:
      pixel, angstrom, angstrom_per_pixel = calibration_elements
      if angstrom in element_lines:
        angstrom = element_lines[angstrom].angstrom
      calibration = SinglePointCalibration(
        CalibrationReference(int(pixel), float(angstrom)),
        float(angstrom_per_pixel)
      )
    else:
      raise ValueError('Unable to parse calibration argument')

    base_spectra.set_calibration(calibration)

  if base_spectra.calibration:

    print base_spectra.calibration

    if args.lines:
      lines_to_plot = args.lines.split(',')

      for line_to_plot in lines_to_plot:
        line = element_lines[line_to_plot]
        plots.append(line)

    graph_subplot.axvline(x=0, color='yellow')
    graph_subplot.set_xlabel(r'Wavelength ($\AA$)')

    if args.reference:
      reference = Reference(args.reference)
      reference.scale_to(base_spectra)
      plots.append(reference)

      # FIXME
      graph_subplot.set_ylim(top=50000)

      plots.append(CorrectedSpectra(base_spectra, reference))

  else:
    graph_subplot.set_xlabel('Pixel')
    

  if args.title:
    title = args.title
  else:
    title = args.filename

  plt.title(title)

  if args.suptitle:
    plt.suptitle(args.suptitle)

  if args.export:
    # FIXME
    export = FitsExport(base_spectra)
    export.writeto(args.export)
  else:
    for plot in plots:
      plot.plot_onto(graph_subplot)

    graph_subplot.legend(loc='best')

    plt.show()

if __name__ == '__main__':
  main()
