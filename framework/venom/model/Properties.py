# package imports
from model import ModelAttribute


__all__  = ['Property', 'PropertyComparison']
__all__ += ['InvalidPropertyComparison']


class PropertyComparison(object):
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
    
    self._values = {}
    
  def validate(self, value):
    if self.required and value == None:
      raise PropertyValidationFailed('Required property was None')
  
  @staticmethod
  def _force_list(value):
    if not isinstance(value, list):
      return [value]
    return value
  
  def _to_search_fields(self):
    return self._force_list(self.to_search_fields())
  
  def to_search_fields(self):
    raise NotImplementedError()
  
  def _to_datastore_properties(self):
    return self._force_list(self.to_datastore_properties())
  
  def to_datastore_properties(self):
    raise NotImplementedError()
  
  def _set_value(self, entity, value):
    self._values[id(entity)] = value
  
  def _get_value(self, entity):
    return self._values[id(entity)]
  
  def _set_stored_value(self, entity, value):
    self._values[id(entity)] = value
  
  def _get_stored_value(self, entity):
    return self._values[id(entity)]
  
  def _on_compare(self, operator):
    # hook for subclasses to react when
    # a comparison is executed
    pass
  
  def _handle_comparison(self, operator, value):
    if not operator in self.allowed_operators:
      raise InvalidPropertyComparison('Property does not support {} comparisons'.format(operator))
    self.compared = True
    self._on_compare(operator)
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
  
  def IN(self, value):
    return self._handle_comparison(PropertyComparison.IN, value)
