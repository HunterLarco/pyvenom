__all__ = ['Parameter']


class ParameterValidationFailed(Exception):
  pass

class ParameterCastingFailed(Exception):
  pass


class Parameter(object):
  _attributes = ['required']
  
  required = True
  
  def __init__(self, required=True):
    self.required = required
  
  def load(self, value):
    if value == None:
      if self.required:
        raise ParameterValidationFailed('Parameter was None when required')
      return None
    
    try:
      value = self.cast(value)
    except:
      raise ParameterCastingFailed('Parameter failed casting')
      
    self.validate(value)
    return value
  
  def cast(self, value):
    return value
  
  def validate(self, value):
    pass
  
  def __iter__(self):
    cls = self.__class__
    yield 'type', cls.__name__
    yield 'attributes', self._get_attributes_dict()
  
  def _get_attributes_dict(self):
    attrs = {}
    for attribute in self._attributes:
      if hasattr(self, attribute):
        value = getattr(self, attribute)
        value = self._recursive_to_dict(value)
        attrs[attribute] = value
    return attrs
  
  def _recursive_to_dict(self, value):
    if isinstance(value, Parameter):
      value = dict(value)
    elif isinstance(value, list):
      value = map(self._recursive_to_dict, value)
    elif isinstance(value, dict):
      value = { key: self._recursive_to_dict(val) for key, val in value.items() }
    return value
  
  def __repr__(self):
    cls = self.__class__
    args = []
    for attr in self._attributes:
      if hasattr(self, attr):
        value = getattr(self, attr)
        if not value == getattr(cls, attr):
          args.append('{}={!r}'.format(attr, value))
    name = cls.__name__
    if not name.endswith('Parameter'):
      name += 'Parameter'
    return '{}({})'.format(name, ', '.join(args))


class ChoicesParameter(Parameter):
  _attributes = Parameter._attributes + ['choices']
  
  choices = None
  
  def __init__(self, required=True, choices=None):
    super(ChoicesParameter, self).__init__(required=required)
    self.choices = choices
  
  def validate(self, value):
    super(ChoicesParameter, self).validate(value)
    self._validate_choices(value)
  
  def _validate_choices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise ParameterValidationFailed('Parameter value not found in allowable choices')


class String(ChoicesParameter):
  _attributes = ChoicesParameter._attributes + ['min', 'max', 'characters']
  
  min = None
  max = None
  characters = None
  
  def __init__(self, required=True, choices=None, min=None, max=None, characters=None):
    super(String, self).__init__(required=required, choices=choices)
    self.min = min
    self.max = max
    self.characters = characters
  
  def cast(self, value):
    return str(value)
  
  def validate(self, value):
    super(String, self).validate(value)
    self._validate_min(value)
    self._validate_max(value)
    self._validate_characters(value)
  
  def _validate_min(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise ParameterValidationFailed('StringParameter value length was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise ParameterValidationFailed('StringParameter value length was greater than max')
  
  def _validate_characters(self, value):
    if self.characters == None: return
    difference = len(set(value) - set(self.characters))
    if difference > 0:
      raise ParameterValidationFailed('StringParameter value used disallowed characters')
  
  
class Integer(ChoicesParameter):
  _attributes = ChoicesParameter._attributes + ['min', 'max']
  
  min = None
  max = None
  
  def __init__(self, required=True, choices=None, min=None, max=None):
    super(Integer, self).__init__(required=required, choices=choices)
    self.min = min
    self.max = max
  
  def cast(self, value):
    return int(value)
  
  def validate(self, value):
    super(Integer, self).validate(value)
    self._validate_min(value)
    self._validate_max(value)
  
  def _validate_min(self, value):
    if self.min == None: return
    if value < self.min:
      raise ParameterValidationFailed('IntegerParameter value was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if value > self.max:
      raise ParameterValidationFailed('IntegerParameter value was greater than max')


class Float(Integer):
  def cast(self, value):
    return float(value)


class Dict(Parameter):
  _attributes = Parameter._attributes + ['template']
  
  template = None
  
  def __init__(self, template, required=True):
    super(Dict, self).__init__(required=required)
    self.template = self._sanitize_template(template)
  
  def _sanitize_template(self, template):
    if not isinstance(template, dict):
      raise Exception('Dict template must be a dict instance')
    return template
  
  def cast(self, value):
    return dict(value)
  
  def validate(self, value):
    super(Dict, self).validate(value)
    self._validate_template(value)
  
  def _validate_template(self, value):
    for key, param in self.template.items():
      if not isinstance(param, Parameter):
        continue
      param_value = value[key] if key in value else None
      value[key] = param.load(param_value)


class List(Parameter):
  _attributes = Parameter._attributes + ['template', 'min', 'max']
  
  min = None
  max = None
  template = None
  
  def __init__(self, template, required=True, min=None, max=None):
    super(List, self).__init__(required=required)
    self.template = self._sanitize_template(template)
    self.min = min
    self.max = max
  
  def _sanitize_template(self, template):
    if isinstance(template, dict):
      return Dict(template)
    elif not isinstance(template, Parameter):
      raise Exception('List template must be a dict or Parameter instance')
    return template
  
  def cast(self, value):
    return list(value)
  
  def validate(self, value):
    super(List, self).validate(value)
    self._validate_min(value)
    self._validate_max(value)
    self._validate_template(value)
  
  def _validate_template(self, value):
    for i, item in enumerate(value):
      value[i] = self.template.load(item)
  
  def _validate_min(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise ParameterValidationFailed('ListParameter value length was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise ParameterValidationFailed('ListParameter value length was greater than max')
