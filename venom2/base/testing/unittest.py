# future
from __future__ import print_function

# PSL imports
import collections
import inspect
import traceback
import sys


__all__ = [
  # Main classes
  'TestCase', 'TestLoader', 'TestResult',
  # Utility classes
  'TerminalColors',
  # Main functions
  'main'
]


class TerminalColors:
  PURPLE    = '\033[95m'
  BLUE      = '\033[94m'
  GREEN     = '\033[92m'
  YELLOW    = '\033[93m'
  RED       = '\033[91m'
  RESET     = '\033[0m'
  BOLD      = '\033[1m'
  UNDERLINE = '\033[4m'
  DIM       = '\033[2m'


class TestResult(object):
  def __init__(
      self,
      testcase,
      unbound_test_function,
      exception_type,
      exception_instance,
      exception_traceback):
    self.testcase = testcase
    self.unbound_test_function = unbound_test_function
    self.exception_type = exception_type
    self.exception_instance = exception_instance
    self.exception_traceback = exception_traceback
    self.full_name = self._get_full_name()
    self.passed = not bool(exception_instance)
  
  def _get_full_name(self):
    return '{}.{}.{}'.format(
        self.testcase.__class__.__module__,
        self.testcase.__class__.__name__,
        self.unbound_test_function.__name__)
  
  def write_summary(self):
    if self.passed:
      return '[=======] {}'.format(self.full_name)
    result = '[       ] {}'.format(self.full_name)
    result += '\n......... {}: {}'.format(self.exception_type.__name__, self.exception_instance)
    error_frames = traceback.extract_tb(self.exception_traceback)
    for file_name, line_number, scope, line_contents in reversed(error_frames):
      result += "\n......... {}:{} in '{}'".format(file_name, line_number, scope)
      result += "\n.........       {}".format(line_contents)
    return result
  
  def __repr__(self):
    summary = 'PASS' if self.passed else 'FAIL'
    return 'TestResult({} {})'.format(summary, self.full_name)


class TestCase(object):
  IGNORE_TEST = False
  FAILURE_EXCEPTION = AssertionError
  
  def setup(self):
    pass # Hook run before every test
  
  def teardown(self):
    pass # Hook after before every test
  
  def assertEqual(self, actual, expected):
    if actual != expected:
      raise self.FAILURE_EXCEPTION('Expected {}\nFound {}'.format(expected, actual))

class TestLoader(object):
  TEST_CASE_CLASS = TestCase
  TEST_METHOD_PREFIX = 'test_'
  
  def __init__(self):
    self._testCases = tuple(self._findSubclasses(self.TEST_CASE_CLASS))
    self._tests = tuple(self._findAllTests())
  
  def _findSubclasses(self, super_class):
    for subclass in super_class.__subclasses__():
      yield subclass
      for sub_subclass in self._findSubclasses(subclass):
        yield sub_subclass
  
  def _findAllTests(self):
    testCaseIndex = collections.defaultdict(dict)
    for testcase in self._testCases:
      if testcase.IGNORE_TEST: continue
      for test_name, test_funct in self.extractTestsFromTestCase(testcase):
        yield test_funct
  
  def extractTestsFromTestCase(self, testcase):
    attributes = dir(testcase)
    for attribute in attributes:
      if attribute.startswith(self.TEST_METHOD_PREFIX):
        value = getattr(testcase, attribute)
        if inspect.ismethod(value):
          yield (attribute, value)
  
  def execute_tests(self):
    results = self.get_all_test_results()
    self.summarize_results(results)
  
  def summarize_results(self, results):
    print('======================================================================')
    print('TEST RESULTS')
    print('----------------------------------------------------------------------')
    
    sorted_results = sorted(results, key=self._result_sorter_key)
    failed = 0
    for result in sorted_results:
      summary = result.write_summary()
      if not result.passed:
        failed += 1
      print(summary)
    
    print('----------------------------------------------------------------------')
    print(TerminalColors.DIM, end='')
    print('[Total Tests] {}'.format(len(sorted_results)), end=' ')
    print('[Passed] {}'.format(len(sorted_results) - failed), end=' ')
    print('[Failed] {}'.format(failed), end=' ')
    print('[Summary] ', end='')
    print(TerminalColors.RESET, end='')
    if failed > 0:
      print(TerminalColors.RED, end='')
      print('FAILED', end='')
    else:
      print(TerminalColors.GREEN, end='')
      print('PASSED', end='')
    print(TerminalColors.RESET)
  
  @staticmethod
  def _result_sorter_key(result):
    return (not result.passed, result.full_name)
  
  def get_all_test_results(self):
    for test in self._tests:
      yield self.execute_test(test)
  
  def execute_test(self, unbound_test_function):
    testcase = unbound_test_function.im_class()
    testcase.setup()
    exception_instance = None
    exception_type = None
    traceback = None
    try:
      unbound_test_function(testcase)
    except Exception:
      exception_type, exception_instance, traceback = sys.exc_info()
      if exception_type == testcase.FAILURE_EXCEPTION:
        pass
    finally:
      testcase.teardown()
    return TestResult(
        testcase,
        unbound_test_function,
        exception_type,
        exception_instance,
        traceback)

  def __repr__(self):
    return 'TestLoader(...)'
  
  def __str__(self):
    suite_count = len(self._testsByNameByTestCase)
    tests = []
    for testcase_name, testcase_data in self._testsByNameByTestCase.items():
      for test_name in testcase_data:
        test_fullname = '{}.{}'.format(testcase_name, test_name)
        tests.append(test_fullname)
    tests.sort()
    result = '======================================================================'
    result += '\nTEST LOADER TESTS'
    result += '\n----------------------------------------------------------------------'
    result += '\n{}'.format('\n'.join(tests))
    result += '\n----------------------------------------------------------------------'
    result += '\nTotal Tests: {}'.format(len(tests))
    result += '\nTotal Test Suites: {}'.format(suite_count)
    return result


def main(default_loader=TestLoader):
  loader = TestLoader()
  loader.execute_tests()


if __name__ == '__main__':
  main()
