# classes
__all__ = ['Parameter', 'Int', 'Float', 'String', 'List', 'Dict']

# exceptions
__all__ += ['ParameterEnforcementFailed', 'ParameterCastingFailed', 'ParameterRequiredException']


class ParameterEnforcementFailed(Exception):
  pass

class ParameterCastingFailed(Exception):
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
    self._options = { 'required': required }
  
  def load(self, value):
    if value == None:
      if self.required:
        raise ParameterRequiredException('Parameter required and cannot be None')
      return value
    
    try:
      value = self.cast(value)
    except Exception:
      raise ParameterCastingFailed('Parameter casting failed')
    
    try:
      self.enforce(value)
    except ParameterEnforcementFailed as err:
      raise err
    except ParameterCastingFailed as err:
      raise err
    except ParameterRequiredException as err:
      raise err
    except Exception as err:
      raise ParameterEnforcementFailed('Unknown exception during parameter enforcing')
    
    return value
  
  def enforce(self, value):
    raise NotImplementedError()
  
  def cast(self, value):
    raise NotImplementedError()
  
  def to_meta_dict(self):
    raise NotImplementedError()
  
  def __repr__(self):
    options = ['{}={}'.format(key, value) for key, value in self._options.items() if value is not None]
    options = ', '.join(options)
    return '{}({})'.format(self.__class__.__name__, options)


class Int(Parameter):
  def __init__(self, min=None, max=None, choices=None, required=True):
    super(Int, self).__init__(required=required)
    self.min = min
    self.max = max
    self.choices = choices
    self._options['min'] = min
    self._options['max'] = max
    self._options['choices'] = choices
  
  def cast(self, value):
    return int(value)
  
  def enforce(self, value):
    self.enforce_min(value)
    self.enforce_max(value)
    self.enforce_choices(value)
  
  def enforce_min(self, value):
    if self.min is None: return
    if value < self.min:
      raise ParameterEnforcementFailed('Int less than minimum')
  
  def enforce_max(self, value):
    if self.max is None: return
    if value > self.max:
      raise ParameterEnforcementFailed('Int greater than minimum')
  
  def enforce_choices(self, value):
    if self.choices is None: return
    if value not in self.choices:
      raise ParameterEnforcementFailed('Int not in enforced choices')
  
  def to_meta_dict(self):
    return removenull({
      'type': 'int',
      'required': self.required,
      'min': self.min,
      'max': self.max,
      'choices': self.choices
    })


class Float(Int):
  def cast(self, value):
    return float(value)
  
  def to_meta_dict(self):
    return removenull({
      'type': 'float',
      'required': self.required,
      'min': self.min,
      'max': self.max,
      'choices': self.choices
    })


class String(Parameter):
  def __init__(self, min=None, max=None, choices=None, characters=None, required=True):
    super(String, self).__init__(required=required)
    self.min = min
    self.max = max
    self.choices = choices
    self.characters = characters
    self._options['min'] = min
    self._options['max'] = max
    self._options['choices'] = choices
    self._options['characters'] = characters
  
  def cast(self, value):
    return str(value)
  
  def enforce(self, value):
    self.enforce_minimum(value)
    self.enforce_maximum(value)
    self.enforce_choices(value)
    self.enforce_characters(value)
  
  def enforce_minimum(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise ParameterEnforcementFailed('String length was less than minimum')
  
  def enforce_maximum(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise ParameterEnforcementFailed('String length exceeded maximum')
  
  def enforce_choices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise ParameterEnforcementFailed('String not found in permitted choices')
  
  def enforce_characters(self, value):
    if self.characters == None: return
    valueset = set(value)
    charset = set(self.characters)
    if len(valueset - charset) > 0:
      raise ParameterEnforcementFailed('String contains illegal characters')
  
  def to_meta_dict(self):
    return removenull({
      'type': 'string',
      'min': self.min,
      'max': self.max,
      'characters': self.characters,
      'choices': self.choices,
      'required': self.required
    })


class Dict(Parameter):
  def __init__(self, template, required=True):
    super(Dict, self).__init__(required=required)
    self._sanitize_template(template)
    self.template = template
    self._options['template'] = template
  
  def _sanitize_template(self, template):
    for key, param in template.items():
      if not isinstance(param, Parameter):
        if isinstance(param, dict):
          template[key] = Dict(param)
        else:
          raise Exception('Unknown Dict parameter template value')
  
  def cast(self, value):
    return dict(value)
  
  def enforce(self, dict_value):
    for key, param in self.template.items():
      if key in dict_value:
        dict_value[key] = param.load(dict_value[key])
      elif param.required:
        raise ParameterRequiredException('Required key in Dict template not found')
  
  def to_meta_dict(self):
    return removenull({
      'type': 'dict',
      'required': self.required,
      'keys': dict(
        [(key, value.to_meta_dict()) for key, value in self.template.items()]
      )
    })


class List(Parameter):
  def __init__(self, template, min=None, max=None, required=True):
    super(List, self).__init__(required=required)
    self.min = min
    self.max = max
    self.template = self._sanitize_template(template)
    self._options['min'] = min
    self._options['max'] = max
    self._options['template'] = template
  
  def _sanitize_template(self, template):
    if not isinstance(template, Parameter):
      if isinstance(template, dict):
        return Dict(template)
      else:
        raise Exception('Unknown Dict parameter template value')
    return template
  
  def cast(self, value):
    return list(value)
  
  def enforce(self, arr):
    if self.min is not None and len(arr) < self.min:
      raise ParameterEnforcementFailed('List length was less than minimum')
    if self.max is not None and len(arr) > self.max:
      raise ParameterEnforcementFailed('List length exceeded maximum')
    
    for i, item in enumerate(arr):
      arr[i] = self.template.load(item)
  
  def to_meta_dict(self):
    return removenull({
      'type': 'list',
      'min': self.min,
      'max': self.max,
      'required': self.required,
      'template': self.template.to_meta_dict()
    })
