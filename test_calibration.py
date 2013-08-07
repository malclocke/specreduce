import unittest
import spectraplot

class MockReference(object):
  pass

class CalibrationTests(unittest.TestCase):

  def setUp(self):
    self.reference1 = MockReference()
    self.reference2 = MockReference()
    self.reference1.pixel = 0
    self.reference1.angstrom = 0
    self.reference2.pixel = 1000
    self.reference2.angstrom = 1000
    self.c = spectraplot.Calibration(self.reference1, self.reference2)

  def testAngstrom(self):
    self.assertEqual(self.c.angstrom(100), 100)

  def testAngstromPerPixel(self):
    self.assertEqual(self.c.angstrom_per_pixel(), 1)

  def testRepr(self):
    self.assertEqual(self.c.__repr__(), "<Calibration angstrom_per_pixel: 1.000000>")


def main():
  unittest.main()

if __name__ == '__main__':
  main()
