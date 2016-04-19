# system imports
import re


__all__ = [
  'Parameter', 'ChoicesParameter', 'String', 'Integer',
  'Float', 'Password', 'Dict', 'List', 'Model'
]


class ParameterValidationFailed(Exception):
  pass

class ParameterCastingFailed(Exception):
  pass


class Parameter(object):
  _attributes = ['required']
  _arguments = []
  
  required = True
  
  def __init__(self, required=True):
    super(Parameter, self).__init__()
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
  
    args = self._get_arguments_dict()
    for key, value in args.items():
      yield key, value
  
    yield 'attributes', self._get_attributes_dict()
  
  def __json__(self):
    return dict(self)
  
  def _get_attributes_dict(self):
    """
    ' Used by __repr__ and __iter__ to get all
    ' properties that should be represented as an attribute
    ' for this object. These are different than arguments.
    ' For example, a List template is an argument whereas
    ' required=False is an attribute.
    """
    attrs = {}
    for attribute in self._attributes:
      if hasattr(self, attribute):
        value = getattr(self, attribute)
        value = self._recursive_to_dict(value)
        attrs[attribute] = value
    return attrs
  
  def _get_arguments_dict(self):
    """
    ' Used by __repr__ and __iter__ to get all
    ' properties that should be represented at a root
    ' level of this object. These are different than attributes.
    ' For example, a List template is an argument whereas
    ' required=False is an attribute.
    """
    args = {}
    for argument in self._arguments:
      if hasattr(self, argument):
        value = getattr(self, argument)
        value = self._recursive_to_dict(value)
        args[argument] = value
    return args
  
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
    attributes = set(self._attributes + self._arguments)
    args = []
    for attr in attributes:
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
  _arguments = Parameter._arguments
  
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
  _attributes = ChoicesParameter._attributes + ['min', 'max', 'characters', 'pattern']
  _arguments = ChoicesParameter._arguments
  
  min = None
  max = None
  characters = None
  pattern = None
  
  def __init__(self, required=True, choices=None, min=None, max=None, characters=None, pattern=None):
    super(String, self).__init__(required=required, choices=choices)
    self.min = min
    self.max = max
    self.characters = characters
    self.pattern = self._sanitize_pattern(pattern)
  
  def _sanitize_pattern(self, pattern):
    if not pattern: return None
    if not pattern.startswith('^'):
      pattern = '^{}'.format(pattern)
    if not pattern.endswith('$'):
      pattern = '{}$'.format(pattern)
    return pattern
  
  def cast(self, value):
    return str(value)
  
  def validate(self, value):
    super(String, self).validate(value)
    self._validate_min(value)
    self._validate_max(value)
    self._validate_characters(value)
    self._validate_pattern(value)
  
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
  
  def _validate_pattern(self, value):
    if self.pattern == None: return
    if not re.match(self.pattern, value):
      raise ParameterValidationFailed('StringParameter did not adhere to pattern')
  
  
class Integer(ChoicesParameter):
  _attributes = ChoicesParameter._attributes + ['min', 'max']
  _arguments = ChoicesParameter._arguments
  
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
  _attributes = Parameter._attributes
  _arguments = Parameter._arguments + ['template']
  
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
  _attributes = Parameter._attributes + ['min', 'max']
  _arguments = Parameter._arguments + ['template']
  
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


class Model(Parameter):
  _attributes = Parameter._attributes
  _arguments = Parameter._arguments + ['modelname']
  
  def __init__(self, model, required=True):
    super(Model, self).__init__(required=required)
    self.model = model
    self.modelname = model.__name__
  
  def cast(self, value):
    value = super(Model, self).cast(value)
    return self.model.get(value)
  
  def validate(self, value):
    super(Model, self).validate(value)
    if not value:
      raise Exception('Entity not found')
