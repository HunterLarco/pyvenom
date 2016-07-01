__all__ = [
  # Main classes
  'AbstractAssertion',
  'EqualityAssertion',
  # Exceptions
  'AssertionExitException'
]


class AssertionExitException(Exception):
  def __init__(self, assertion):
    super(AssertionExitException, self).__init__(
        'AssertionExitException triggered by {}'.format(assertion))
    self.assertion = assertion


class AbstractAssertion(object):
  def __init__(self):
    super(AbstractAssertion, self).__init__()
    self.cached_error_message = None
  
  @property
  def ERROR_MESSAGE(self):
    raise NotImplementedError
  
  def do_assertion(self, *args):
    raise NotImplementedError
  
  def get_error_message(self, *args):
    raise NotImplementedError
  
  def cache_error_message(self, *args, **kwargs):
    if self.cached_error_message: return self.cached_error_message
    message = self.get_error_message(*args, **kwargs)
    self.cached_error_message = message
    return message


class EqualityAssertion(AbstractAssertion):
  ERROR_MESSAGE = (
      'Equality Assertion Failed.',
      'Expected',
      '    {expected}',
      'Found',
      '    {actual}')
  
  def do_assertion(self, actual, expected):
    return actual == expected
  
  def get_error_message(self, actual, expected):
    return self.ERROR_MESSAGE.format({
      'actual': actual,
      'expected': expected
    })
