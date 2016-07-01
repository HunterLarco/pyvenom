__all__ = [
  # Main classes
  'AbstractTestResult', 'PassedTestResult', 'CaughtTestResult', 'UncaughtTestResult'
]


class AbstractTestResult(object):
  def __init__(self, unittest):
    super(AbstractTestResult, self).__init__()
    self.unittest = unittest
  
  @property
  def passed(self):
    raise NotImplementedError
  
  def get_result_summary(self):
    '''
    PURPOSE
      Used by TestSummarizer to describe a test's result
    PARAMETERS
      None
    RETURNS
      str    A string describing the results of this test
    '''
    raise NotImplementedError


class PassedTestResult(AbstractTestResult):
  passed = True
  
  def get_result_summary(self):
    return '{} Passed'.format(unittest.full_name)


class CaughtTestResult(AbstractTestResult):
  passed = False
  
  def __init__(self, unittest, failed_assertion):
    super(CaughtTestResult, self).__init__(unittest)
    self.failed_assertion = failed_assertion
  
  def get_result_summary(self):
    if not self.failed_assertion.cached_error_message:
      raise Exception("Assertion attribute 'cached_error_message' unexpectedly None")
    return self.failed_assertion.cached_error_message


class UncaughtTestResult(AbstractTestResult):
  passed = False
  
  def __init__(self, unittest, exception_instance, exception_traceback):
    super(UncaughtTestResult, self).__init__(unittest)
    self.exception_instance = exception_instance
    self.exception_traceback = exception_traceback
  
  def get_result_summary(self):
    # TODO(hunterlarco)
    return 'Uncaught exception'
    
