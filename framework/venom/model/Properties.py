# app engine imports
from google.appengine.ext import ndb

# package imports
from attribute import ModelAttribute
from query import PropertyComparison


__all__  = ['Property']
__all__ += ['InvalidPropertyComparison', 'PropertyValidationFailed']


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
  
  def _to_datastore_property(self):
    prop = self.to_datastore_property()
    if issubclass(prop, ndb.Property):
      prop = prop()
    prop._indexed = self.datastore
    return prop
  
  def to_datastore_property(self):
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
    entity._values[self._name] = self._from_storage(value)
  
  def _get_stored_value(self, entity):
    return self._to_storage(entity._values[self._name])
  
  def _to_storage(self, value):
    return value
  
  def _from_storage(self, value):
    return value
  
  def query_uses_datastore(self, operator, value):
    raise NotImplementedError()
  
  def _handle_comparison(self, operator, value):
    if not operator in self.allowed_operators:
      raise InvalidPropertyComparison('Property does not support {} comparisons'.format(operator))
    self.compared = True
    
    uses_datastore = self.query_uses_datastore(operator, value)
    if uses_datastore:
      self.datastore = True
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
