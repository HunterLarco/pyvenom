__all__ = ['Property', 'String']
__all__ += ['QueryNotSupported', 'InvalidModelPropertyConnection', 'PropertyEnforcementFailed', 'InvalidPropertyInitialization']
__all__ += ['PropertyQuery']


class PropertyQuery(object):
  EQ = '=='
  NE = '!='
  LT = '<'
  LE = '<='
  GT = '>'
  GE = '>='
  
  def __init__(self, prop, operator, value):
    self.prop = prop
    self.operator = operator
    self.value = value


class QueryNotSupported(Exception):
  pass

class InvalidModelPropertyConnection(Exception):
  pass

class PropertyEnforcementFailed(Exception):
  pass

class InvalidPropertyInitialization(Exception):
  pass


class Property(object):
  def __init__(self, required=False, default=None, choices=None):
    if required and default != None:
      raise InvalidPropertyInitialization('Property have a default value if required')
    
    self.required = required
    self.default = default
    self.choices = choices
    
    self.is_queried = False
    self.ndb = True
    self.search = False
    
    self._name = None
    self._model = None
    self._model_instance = None
  
  def _connect_to_model(self, name, model):
    self._name = name
    self._model = model
  
  def _connect_to_instance(self, model_instance):
    self._model_instance = model_instance
  
  def to_search_field(self):
    raise NotImplementedError()
  
  def to_ndb_property(self):
    raise NotImplementedError()
  
  def enforce(self):
    value = self.get_value()
    
    # required and default
    if not value:
      if self.required:
        raise PropertyEnforcementFailed('Value missing when required')
      value = self.default
    
    # choices
    if self.choices != None:
      if value not in self.choices:
        raise PropertyEnforcementFailed('Value not in required choices')
    
    return value
  
  def get_value(self):
    if self._name == None or self._model == None:
      raise InvalidModelPropertyConnection('Property not connected to Model Class')
    if self._model_instance == None:
      raise InvalidModelPropertyConnection('Property not connected to Model Instance')
    if not hasattr(self._model_instance, self._name):
      raise InvalidModelPropertyConnection('Model missing Property')
    return getattr(self._model_instance, self._name)
  
  def __eq__(self, value):
    raise QueryNotSupported('Property does not support == queries')
  
  def __ne__(self, value):
    raise QueryNotSupported('Property does not support != queries')
  
  def __lt__(self, value):
    raise QueryNotSupported('Property does not support < queries')
  
  def __le__(self, value):
    raise QueryNotSupported('Property does not support <= queries')
  
  def __gt__(self, value):
    raise QueryNotSupported('Property does not support > queries')
  
  def __ge__(self, value):
    raise QueryNotSupported('Property does not support >= queries')
  
  def __repr__(self):
    classname = self.__class__.__name__
    if self._model_instance != None:
      return '{}(name={}, value={})'.format(classname, self._name, self.get_value())
    return '{}(name={})'.format(classname, self._name)
  

class String(Property):
  def __init__(self, required=False, default=None, min=None, max=None, characters=None, choices=None):
    super(String, self).__init__(required=required, default=default, choices=choices)
    self.min = min
    self.max = max
    self.characters = characters
  
  def enforce(self):
    value = super(String, self).enforce()
    if value == None: return value
    
    # type str
    if not isinstance(value, str):
      raise PropertyEnforcementFailed('StringProperty must be of type str')
    
    # min
    if self.min != None and len(value) < self.min:
      raise PropertyEnforcementFailed('StringProperty value less than minimum character length')
    
    # max
    if self.max != None and len(value) > self.max:
      raise PropertyEnforcementFailed('StringProperty value greater than maximum character length')
    
    # characters
    if self.characters != None and len(set(value) - set(self.characters)) > 0:
      raise PropertyEnforcementFailed('StringProperty value contains characters not permitted from "{}"'.format(self.characters))
    
    return value
  
  def __eq__(self, value):
    self.is_queried = True
    return PropertyQuery(self, PropertyQuery.EQ, value)
    
    
    
    

