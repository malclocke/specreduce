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

  can_plot_image = False

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
  can_plot_image = True

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
