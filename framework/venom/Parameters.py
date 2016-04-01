__all__ = ['Parameter', 'String', 'Int', 'Float', 'List']


class ParameterSanitizationException(Exception):
  pass

class ParameterCastingException(Exception):
  pass

class ParameterRequiredException(Exception):
  pass


def removenull(obj):
  for key, value in obj.items():
    if value == None:
      del obj[key]
    if isinstance(value, dict):
      removenull(value)
  return obj


class Parameter(object):
  def __init__(self, required=True):
    self.required = required
  
  def dispatch(self, value):
    if value == None:
      if self.required:
        raise ParameterRequiredException('Parameter required but not found')
      return value
    
    try:
      value = self.cast(value)
    except Exception:
      raise ParameterCastingException('Parameter casting failed')
    
    try:
      value = self.sanitize(value)
    except ParameterCastingException as err:
      raise err
    except ParameterSanitizationException as err:
      raise err
    except ParameterRequiredException as err:
      raise err
    except Exception:
      raise ParameterSanitizationException('Unknown exception during sanitization')
    
    return value
  
  def cast(self, value):
    raise NotImplemented()
  
  def sanitize(self, value):
    raise NotImplemented()
  
  def __repr__(self):
    options = 'required=' + str(self.required)
    return 'Parameter({})'.format(options)
  
  def metadict(self):
    raise NotImplemented()


class String(Parameter):
  def __init__(self, min=None, max=None, choices=None, characters=None, required=True):
    super(String, self).__init__(required=required)
    self.min = min
    self.max = max
    self.choices = choices
    self.characters = characters
  
  def cast(self, value):
    return value
  
  def sanitize(self, value):
    self.enforceMinimum(value)
    self.enforceMaximum(value)
    self.enforceChoices(value)
    self.enforceCharacters(value)
    return value
  
  def enforceMinimum(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise ParameterSanitizationException('String length was less than minimum')
  
  def enforceMaximum(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise ParameterSanitizationException('String length exceeded maximum')
  
  def enforceChoices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise ParameterSanitizationException('String not found in permitted choices')
  
  def enforceCharacters(self, value):
    if self.characters == None: return
    valueset = set(value)
    charset = set(self.characters)
    if len(valueset - charset) > 0:
      raise ParameterSanitizationException('String contains illegal characters')
  
  def __repr__(self):
    options = ''
    if self.min != None: options += 'min=' + str(self.min) + ', '
    if self.max != None: options += 'max=' + str(self.max) + ', '
    if self.choices != None: options += 'choices=' + str(self.choices) + ', '
    if self.characters != None: options += 'characters=' + str(self.characters) + ', '
    options += 'required=' + str(self.required) + ', '
    return 'StringParameter({})'.format(options[:-2])
  
  def metadict(self):
    return removenull({
      'type': 'string',
      'min': self.min,
      'max': self.max,
      'characters': self.characters,
      'choices': self.choices,
      'required': self.required
    })


class Int(Parameter):
  def __init__(self, min=None, max=None, choices=None, required=True):
    super(Int, self).__init__(required=required)
    self.min = min
    self.max = max
    self.choices = choices
  
  def cast(self, value):
    return int(value)
  
  def sanitize(self, value):
    self.enforceMinimum(value)
    self.enforceMaximum(value)
    self.enforceChoices(value)
    return value
  
  def enforceMinimum(self, value):
    if self.min == None: return
    if value < self.min:
      raise ParameterSanitizationException('Int was less than minimum')
  
  def enforceMaximum(self, value):
    if self.max == None: return
    if value > self.max:
      raise ParameterSanitizationException('Int exceeded maximum')
  
  def enforceChoices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise ParameterSanitizationException('Int not found in permitted choices')
  
  def __repr__(self):
    options = ''
    if self.min != None: options += 'min=' + str(self.min) + ', '
    if self.max != None: options += 'max=' + str(self.max) + ', '
    if self.choices != None: options += 'choices=' + str(self.choices) + ', '
    options += 'required=' + str(self.required) + ', '
    return 'IntParameter({})'.format(options[:-2])
  
  def metadict(self):
    return removenull({
      'type': 'int',
      'min': self.min,
      'max': self.max,
      'choices': self.choices,
      'required': self.required
    })


class Float(Int):
  def cast(self, value):
    return float(value)
  
  def __repr__(self):
    options = ''
    if self.min != None: options += 'min=' + str(self.min) + ', '
    if self.max != None: options += 'max=' + str(self.max) + ', '
    if self.choices != None: options += 'choices=' + str(self.choices) + ', '
    options += 'required=' + str(self.required) + ', '
    return 'FloatParameter({})'.format(options[:-2])
  
  def metadict(self):
    return removenull({
      'type': 'float',
      'min': self.min,
      'max': self.max,
      'choices': self.choices,
      'required': self.required
    })


class Dict(Parameter):
  def __init__(self, template, required=True):
    super(Dict, self).__init__(required=required)
    self.template = template
  
  def cast(self, value):
    return dict(value)
  
  def sanitize(self, passedDict):
    for key, value in self.template.items():
      if isinstance(value, Parameter):
        if not key in passedDict:
          if value.required:
            raise ParameterSanitizationException('Dict missing expected parameter {}'.format(key))
        else:
          passedDict[key] = value.dispatch(passedDict[key])
      elif isinstance(value, dict):
        self.__class__(value).dispatch(passedDict[key])
    return passedDict
  
  def __repr__(self):
    return 'DictParameter({})'.format(str(self.template))
  
  def metadict(self):
    return removenull({
      'type': 'dict',
      'required': self.required,
      'children': dict(
        [(key, value.metadict()) for key, value in self.template.items()]
      )
    })


class List(Parameter):
  def __init__(self, template, min=None, max=None, required=True):
    super(List, self).__init__(required=required)
    self.min = min
    self.max = max
    self.template = template
  
  def cast(self, value):
    return list(value)
  
  def sanitize(self, arr):
    if self.min is not None and len(arr) < self.min:
      raise ParameterSanitizationException('List length was less than minimum')
    if self.max is not None and len(arr) > self.max:
      raise ParameterSanitizationException('List length exceeded maximum')
    
    dictparam = Dict(self.template)
    for item in arr:
      dictparam.dispatch(item)
    return arr
  
  def __repr__(self):
    return 'ListParameter({})'.format(str(self.template))
  
  def metadict(self):
    return removenull({
      'type': 'list',
      'min': self.min,
      'max': self.min,
      'required': self.required,
      'template': Dict(self.template).metadict()
    })
