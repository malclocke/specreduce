import unittest
import spectraplot

class ElementLineTests(unittest.TestCase):

  def setUp(self):
    self.el = spectraplot.ElementLine(4861, 'Hb')

  def testAngstrom(self):
    self.assertEqual(self.el.angstrom, 4861)

  def testLabel(self):
    self.assertEqual(self.el.label, 'Hb')

  def testRepr(self):
    self.assertEqual(self.el.__repr__(), '4861.000000 (Hb)')

def main():
  unittest.main()

if __name__ == '__main__':
  main()
