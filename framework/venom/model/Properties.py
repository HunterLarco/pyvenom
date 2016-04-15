# package imports
from model import ModelAttribute
from query import QueryComponent, QueryParameter


__all__  = ['Property', 'PropertyComparison']
__all__ += ['InvalidPropertyComparison']


class PropertyComparison(QueryComponent):
  EQ = '='
  NE = '!='
  LT = '<'
  LE = '<='
  GT = '>'
  GE = '>='
  IN = 'in'
  
  allowed_operators = frozenset((EQ, NE, LT, LE, GT, GE, IN))
  
  def __init__(self, property, operator, value):
    if not operator in self.allowed_operators:
      raise Exception('Unknown operator "{}"'.format(operator))
    
    self.property = property
    self.operator = operator
    self.value = value
  
  """ [below] Implemented from QueryComponent """
  
  def uses_datastore(self):
    return self.property.query_uses_datastore(self.operator, self.value)
  
  def get_property_comparisons(self):
    return [self]
  
  def to_datastore_query(self, args, kwargs):
    prop = self.property.to_datastore_property(self.operator, self.value)
    value = self.value
    if isinstance(self.value, QueryParameter):
      value = self.value.get_value(args, kwargs)
    if   self.operator == self.EQ: return prop == value
    elif self.operator == self.NE: return prop != value
    elif self.operator == self.LT: return prop < value
    elif self.operator == self.LE: return prop <= value
    elif self.operator == self.GT: return prop > value
    elif self.operator == self.GE: return prop >= value
    elif self.operator == self.IN: return prop.IN(value)
    else: raise Exception('Unknown operator')
  
  def to_search_api_query(self, args, kwargs):
    prop = self.property.to_search_field(self.operator, self.value)
    value = self.value
    if isinstance(self.value, QueryParameter):
      value = self.value.get_value(args, kwargs)
    if isinstance(value, str):
      value = '{}'.format(value.replace('"', '\\"'))
    if self.operator == self.NE:
      return '(NOT {} = {})'.format(self.property._name, value)
    return '{} {} {}'.format(self.property._name, self.operator, value)
  
  """ [end] QueryComponent implementation """


class InvalidPropertyComparison(Exception):
  pass

class PropertyValidationFailed(Exception):
  pass


class Property(ModelAttribute):
  allowed_operators = frozenset()
  
  def __init__(self, required=False):
    super(Property, self).__init__()
    
    self.required = required
    
    self.search = False
    self.datastore = False
    self.compared = False
    
    self.search_fields = set()
    self.datastore_properties = set()
    
    self._values = {}
  
  def _connect(self, entity=None, name=None, model=None):
    super(Property, self)._connect(entity=entity, name=name, model=model)
    if entity and not hasattr(entity, '_values'):
      setattr(entity, '_values', {})
  
  def validate(self, value):
    if self.required and value == None:
      raise PropertyValidationFailed('Required property was None')
  
  @staticmethod
  def _force_list(value):
    if not isinstance(value, list):
      return [value]
    return value
  
  def to_search_field(self, operator, value):
    raise NotImplementedError()
  
  def to_datastore_property(self, operator, value):
    raise NotImplementedError()
  
  def __get__(self, instance, cls):
    if instance == None:
      # called on a class
      return self
    return self._get_value(instance)

  def __set__(self, instance, value):
    return self._set_value(instance, value)
  
  def _set_value(self, entity, value):
    entity._values[self._name] = value
  
  def _get_value(self, entity):
    return entity._values[self._name]
  
  def _set_stored_value(self, entity, value):
    entity._values[self._name] = value
  
  def _get_stored_value(self, entity):
    return entity._values[self._name]
  
  def query_uses_datastore(self, operator, value):
    raise NotImplementedError()
  
  def _handle_comparison(self, operator, value):
    if not operator in self.allowed_operators:
      raise InvalidPropertyComparison('Property does not support {} comparisons'.format(operator))
    self.compared = True
    
    uses_datastore = self.query_uses_datastore(operator, value)
    if uses_datastore:
      self.datastore = True
      datastore_property = self.to_datastore_property(operator, value)
      self.datastore_properties.add(datastore_property)
    else:
      self.search = True
      search_field = self.to_search_field(operator, value)
      self.search_fields.add(search_field)
    
    return PropertyComparison(self, operator, value)
  
  def __eq__(self, value):
    return self._handle_comparison(PropertyComparison.EQ, value)

  def __ne__(self, value):
    return self._handle_comparison(PropertyComparison.NE, value)

  def __lt__(self, value):
    return self._handle_comparison(PropertyComparison.LT, value)

  def __le__(self, value):
    return self._handle_comparison(PropertyComparison.LE, value)

  def __gt__(self, value):
    return self._handle_comparison(PropertyComparison.GT, value)

  def __ge__(self, value):
    return self._handle_comparison(PropertyComparison.GE, value)
  
  def contains(self, value):
    return self._handle_comparison(PropertyComparison.IN, value)
