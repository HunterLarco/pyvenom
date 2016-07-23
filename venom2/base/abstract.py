# PSL imports
import functools


__all__ = [
  'NotImplemented'
]


def NotImplemented(funct):
  '''
  ' PURPOSE
  '   Decorator that replaces the given function with
  '   one that throws a NotImplementedError.
  '''
  function_name = funct.__name__
  @functools.wraps(funct)
  def AbstractMethod(*args, **kwargs):
    raise NotImplementedError("'{}' Not Implemented".format(function_name))
  return AbstractMethod
