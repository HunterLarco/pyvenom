import unittest

from helper import smart_assert


class TestCaseHelperTest(unittest.TestCase):
  def setUp(self):
    pass

  def test_equals(self):
    smart_assert(1, 1, 1, 1, 1).equals('This should pass for equality')
    with self.assertRaises(AssertionError) as context:
      smart_assert(1, 1, 1, 1, 2).equals('This should fail for inequality')
  
  def test_not_equals(self):
    smart_assert(1, 2, 3, 4, 5).not_equals('This should pass for inequality')
    with self.assertRaises(AssertionError) as context:
      smart_assert(1, 2, 3, 4, 1).not_equals(message='This should fail for equality')
  
  def test_true(self):
    smart_assert(1, 2, 3, 4, True).true('This should pass since all are True')
    with self.assertRaises(AssertionError) as context:
      smart_assert(1, 2, 3, 4, False).true('This should fail since not all are True')
  
  def test_false(self):
    smart_assert(0, False).false('This should pass since all are False')
    with self.assertRaises(AssertionError) as context:
      smart_assert(False, True).false('This should fail since not all are False')
  
  def test_raises(self):
    with smart_assert.raises(Exception) as context:
      raise Exception('This should not show up')
    
    with self.assertRaises(ValueError) as _context:
      with smart_assert.raises(Exception) as context:
        raise ValueError('This should show up')


if __name__ == '__main__':
  unittest.main()