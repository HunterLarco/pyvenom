__all__ = [
  'RequiredParameterMissingException',
  'InvalidModelIDException',
  'ModelUnpackingFailedException',
  'InvalidNumberOfParameters',
  'ParameterDict'
]


class RequiredParameterMissingException(Exception):
  pass

class InvalidModelIDException(Exception):
  pass

class ModelUnpackingFailedException(Exception):
  pass

class InvalidNumberOfParameters(Exception):
  pass


class ParameterDict(object):
  def __init__(self, params=None):
    self.params = params if params != None else {}
  
  def __repr__(self):
    params = ['{}={}'.format(key, value) for key, value in self.params.items()]
    return '{}({})'.format(self.__class__.__name__, ', '.join(params))
  
  def __getitem__(self, key):
    return self.params[key]
  
  def __setitem__(self, key, value):
    self.params[key] = value
  
  def __delitem__(self, key):
    del self.params[key]
  
  def require(self, *params):
    arr = []
    for param in params:
      if not param in self.params:
        raise RequiredParameterMissingException('Required parameter not found')
      arr.append(self.params[param])
    return arr[0] if len(arr) == 1 else arr
  
  def maybe(self, *params):
    arr = []
    for param in params:
      arr.append(self.params[param] if param in self.params else None)
    return arr[0] if len(arr) == 1 else arr
  
  def choose(self, *params, **kwargs):
    arr = []
    found = 0
    count = kwargs.pop('count', 1)
    for param in params:
      if not param in self.params:
        arr.append(None)
      else:
        found += 1
        if found > count: raise InvalidNumberOfParameters()
        arr.append(self.params[param])
    if found != count: raise InvalidNumberOfParameters()
    return arr[0] if len(arr) == 1 else arr

