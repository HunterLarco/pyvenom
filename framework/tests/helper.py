# system imports
import unittest

# app engine imports
from google.appengine.api import memcache
from google.appengine.ext import ndb
from google.appengine.api.search import simple_search_stub
from google.appengine.ext import testbed


__all__ = ['smart_assert', 'RaiseContext', 'BasicTestCase']


class BasicTestCase(unittest.TestCase):
  def setUp(self):
    # First, create an instance of the Testbed class.
    self.testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    self.testbed.activate()
    # Next, declare which service stubs you want to use.
    self.testbed.init_datastore_v3_stub()
    self.testbed.init_memcache_stub()
    self.testbed.init_search_stub()
    # Clear ndb's in-context cache between tests.
    # This prevents data from leaking between tests.
    # Alternatively, you could disable caching by
    # using ndb.get_context().set_cache_policy(False)
    ndb.get_context().clear_cache()
  
  def tearDown(self):
    self.testbed.deactivate()


class smart_assert(object):
  def __init__(self, *args):
    self.args = args
  
  def type(self, type_cls, message=None):
    if message: assert self._type(type_cls), message
    else: assert self._type(type_cls)
  
  def _type(self, type_cls):
    for value in self.args:
      if not isinstance(value, type_cls):
        return False
    return True
  
  def equals(self, message=None):
    if message: assert self._equals(), message
    else: assert self._equals()
  
  def _equals(self):
    if len(self.args) == 0: return True
    main_value = self.args[0]
    for value in self.args[1:]:
      if value != main_value:
        return False
    return True
  
  def not_equals(self, message=None):
    if message: assert self._not_equals(), message
    else: assert self._not_equals()
  
  def _not_equals(self):
    if len(self.args) == 0: return True
    main_value = self.args[0]
    for value in self.args[1:]:
      if value == main_value:
        return False
    return True
  
  def false(self, message=None):
    if message: assert self._false(), message
    else: assert self._false()
  
  def _false(self):
    for value in self.args:
      if value:
        return False
    return True
  
  def true(self, message=None):
    if message: assert self._true(), message
    else: assert self._true()
  
  def _true(self):
    for value in self.args:
      if not value:
        return False
    return True
  
  @staticmethod
  def raises(*exceptions, **kwargs):
    message = kwargs['message'] if 'message' in kwargs else None
    return RaiseContext(exceptions, message=message)
  
  
class RaiseContext():
  def __init__(self, exceptions, message=None):
    self.exceptions = exceptions
    self.message = message
  
  def __enter__(self):
    return self
  
  def __exit__(self, exception_type, exception_value, exception_traceback):
    if self.exceptions:
      return self._when_exception_required(exception_type)
    return self._when_exception_not_required(exception_type)
  
  def _when_exception_not_required(self, exception_type):
    if exception_type == None:
      return False
    assert False, 'Exception of type {} thrown when exceptions should not have been thrown'.format(exception_type)
  
  def _when_exception_required(self, exception_type):
    if exception_type == None:
      assert False, 'No exception thrown when expected from list {!r}'.format(self.exceptions)
    if not exception_type in self.exceptions:
      return False
    return True
