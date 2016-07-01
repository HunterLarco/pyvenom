# future
from __future__ import print_function

# venom imports
from venom2.base.testing import assertions
from venom2.base.testing import results

# PSL imports
import collections
import inspect
import traceback
import sys


__all__ = [
  # Main classes
  'TestSuite', 'TestCase', 'UnitTest',
  'TestSummarizer',
]


class UnitTest(object):
  def __init__(self, testcase_class, unbound_function):
    self.testcase_class = testcase_class
    self._unbound_function = unbound_function
    self.result = None
    self.has_run = False
  
  def do_test(self):
    testcase_instance = self.testcase_class()
    # TODO(hunterlarco) provide custom traceback for setup failure
    testcase_instance.setup()
    try:
      self._unbound_function(testcase_instance)
      self.result = results.PassedTestResult(self)
    except assertions.AssertionExitException as assertion_exception:
      failed_assertion = assertion_exception.assertion
      self.result = results.CaughtTestResult(self, failed_assertion)
    except Exception as exception:
      exception_type, exception_instance, traceback = sys.exc_info()
      self.result = results.UncaughtTestResult(self, exception_instance, traceback)
    finally:
      # TODO(hunterlarco) provide custom traceback for teardown failure
      testcase_instance.teardown()
      self.has_run = True
    if self.result == None:
      raise Exception('Test result unexpectedly None')
  
  @property
  def full_name(self):
    return '{}.{}'.format(self.testcase_class.full_name, self.name)
  
  @property
  def name(self):
    return self._unbound_function.__name__


class TestCaseMetaClass(type):
  def __init__(cls, name, bases, classdict):
    super(TestCaseMetaClass, cls).__init__(name, bases, classdict)
    cls._init_cls()


class TestCase(object):
  __metaclass__ = TestCaseMetaClass
  
  TEST_PREFIX = 'test_'
  
  @classmethod
  def _init_cls(cls):
    self.name = cls.__name__
    self.full_name = '{}.{}'.format(cls.__module__, cls.__name__)
    self.unittests = frozenset(self._load_unittests())
  
  def __init__(self, testsuite):
    self.testsuite = testsuite
  
  @classmethod
  def _load_unittests(cls):
    attributes = dir(cls)
    for attribute in attributes:
      if not attribute.startswith(TEST_PREFIX): continue
      value = getattr(cls, attribute)
      if not inspect.ismethod(value): continue
      yield UnitTest(cls, value)


class TestSuite(object):
  pass
