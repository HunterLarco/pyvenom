# app engine imports
from google.appengine.ext import ndb
from google.appengine.api import search

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
  allowed_types = frozenset()
  
  def __init__(self, required=False):
    super(Property, self).__init__()
    self.required = required
  
  def _connect(self, entity=None, name=None, model=None):
    super(Property, self)._connect(entity=entity, name=name, model=model)
    if entity and not hasattr(entity, '_values'):
      setattr(entity, '_values', {})
  
  def validate(self, value):
    if self.required and value == None:
      raise PropertyValidationFailed('Required property was None')
    
    if len(self.allowed_types) > 0:
      for allowed_type in self.allowed_types:
        if isinstance(value, allowed_type):
          break
      else:
        raise PropertyValidationFailed('Property value does not conform to allowed_types')
  
  @staticmethod
  def _force_list(value):
    if not isinstance(value, list):
      return [value]
    return value
  
  def to_search_field(self):
    raise NotImplementedError()
  
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
    self.validate(value)
    entity._values[self._name] = value
  
  def _get_value(self, entity):
    if not self._name in entity._values:
      return None
    return entity._values[self._name]
  
  def _set_stored_value(self, entity, value):
    entity._values[self._name] = self._from_storage(value)
  
  def _get_stored_value(self, entity):
    if not self._name in entity._values:
      value = None
    else:
      value = entity._values[self._name]
    return self._to_storage(value)
  
  def _to_storage(self, value):
    return value
  
  def _from_storage(self, value):
    return value
  
  def query_uses_datastore(self, operator, value):
    raise NotImplementedError()
  
  def _handle_comparison(self, operator, value):
    if not operator in self.allowed_operators:
      raise InvalidPropertyComparison('Property does not support {} comparisons'.format(operator))
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


class ChoicesProperty(Property):
  def __init__(self, required=False, choices=None):
    super(ChoicesProperty, self).__init__(required=required)
    self.choices = choices
  
  def validate(self, value):
    super(ChoicesProperty, self).validate(value)
    self._validate_choices(value)
  
  def _validate_choices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise PropertyValidationFailed('Parameter value not found in allowable choices')


class Integer(ChoicesProperty):
  allowed_operators = PropertyComparison.allowed_operators
  allowed_types = frozenset({int})
  
  def __init__(self, required=False, choices=None, min=None, max=None):
    super(Integer, self).__init__(required=required, choices=choices)
    self.min = min
    self.max = max
    
  def _from_storage(self, value):
    if value == None:
      return None
    return int(value)
    
  def validate(self, value):
    super(Integer, self).validate(value)
    if value == None: return
    self._validate_min(value)
    self._validate_max(value)
  
  def _validate_min(self, value):
    if self.min == None: return
    if value < self.min:
      raise PropertyValidationFailed('IntegerProperty value length was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if value > self.max:
      raise PropertyValidationFailed('IntegerProperty value length was greater than max')

  def query_uses_datastore(self, operator, value):
    return True
        
  def to_search_field(self):
    return search.NumberField
  
  def to_datastore_property(self):
    return ndb.IntegerProperty
    

class Float(Integer):
  allowed_types = frozenset((float, int))
  
  def _to_storage(self, value):
    if value == None:
      return None
    return float(value)
  
  def _from_storage(self, value):
    if value == None:
      return None
    return float(value)
  
  def to_datastore_property(self):
    return ndb.FloatProperty


class String(ChoicesProperty):
  allowed_operators = PropertyComparison.allowed_operators
  allowed_types = [str, unicode]
  
  def __init__(self, required=False, choices=None, min=None, max=500, characters=None):
    super(String, self).__init__(required=required, choices=choices)
    self.min = min
    self.max = max
    self.characters = characters
  
  def _to_storage(self, value):
    return str(value)
  
  def _from_storage(self, value):
    return str(value)
  
  def validate(self, value):
    super(String, self).validate(value)
    if value == None: return
    self._validate_type(value)
    self._validate_min(value)
    self._validate_max(value)
    self._validate_characters(value)

  def _validate_type(self, value):
    if not isinstance(value, str) and not isinstance(value, unicode):
      raise PropertyValidationFailed('StringProperty value must be an str or unicode instance')
  
  def _validate_min(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise PropertyValidationFailed('IntegerProperty value length was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise PropertyValidationFailed('IntegerProperty value length was greater than max')
  
  def _validate_characters(self, value):
    if self.characters == None: return
    difference = len(set(value) - set(self.characters))
    if difference > 0:
      raise PropertyValidationFailed('StringProperty value used disallowed characters')

  def query_uses_datastore(self, operator, value):
    return self.max != None and self.max <= 500
  
  def to_search_field(self):
    return search.TextField
  
  def to_datastore_property(self):
    return ndb.StringProperty


class Password(String):
  def _hash(self, value):
    import hashlib
    return hashlib.sha256(value).hexdigest()
  
  def _set_value(self, entity, value):
    self.validate(value)
    entity._values[self._name] = self._hash(value)

  def _get_stored_value(self, entity):
    return self._get_value(entity)

  def _to_storage(self, value):
    return self._hash(value)


class Model(Property):
  def __init__(self, model, required=False):
    super(Model, self).__init__(required=required)
    self.model = model

  def _get_value(self, entity):
    value = super(Model, self)._get_value(entity)
    if not isinstance(value, self.model):
      value = self.model.get(value)
    self._set_value(entity, value)
    return value

  def _to_storage(self, value):
    if value == None:
      return None
    if isinstance(value, self.model):
      return value.key
    return value
  
  def to_search_field(self):
    return search.TextField
  
  def to_datastore_property(self):
    return ndb.StringProperty
  
  def query_uses_datastore(self, operator, value):
    return True
