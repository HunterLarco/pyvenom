# package imports
from venom2.base.collections import enum
from venom2.base.testing import unittest


__all__ = [
  # Main classes
  'EnumTests',
  # commandline entry function
  'main'
]


class EnumTests(unittest.TestCase):
  def setup(self):
    self.FooBar = enum.Enum('FooBar', ['Foo', 'Bar', 'Baz'])
  
  def test_repr(self):
    self.assertEqual(repr(self.FooBar), '<Enum FooBar>')
    self.assertEqual(repr(self.FooBar.Foo), '<EnumValue FooBar.Foo>')
    self.assertEqual(repr(self.FooBar.Bar), '<EnumValue FooBar.Bar>')
    self.assertEqual(repr(self.FooBar.Baz), '<EnumValue FooBar.Baz>')
  
  def test_unknown(self):
    pass


def main():
  unittest.main()


if __name__ == '__main__':
  main()
