# app engine imports
from google.appengine.ext import ndb
from google.appengine.api import search

# package imports
from attribute import ModelAttribute
from query import PropertyComparison, Query, QueryParameter
from ..routing import Parameters


__all__  = ['Property']
__all__ += ['InvalidPropertyComparison', 'PropertyValidationFailed']


class InvalidPropertyComparison(Exception):
  pass

class PropertyValidationFailed(Exception):
  pass


class Property(ModelAttribute):
  allowed_operators = frozenset()
  allowed_types = frozenset()
  
  def __init__(self, required=False, hidden=False, unique=False):
    super(Property, self).__init__()
    self.required = required
    self.hidden = hidden
    self.unique = unique
  
  def __equals__(self, value):
    cls = self.__class__
    if not isinstance(value, cls):
      raise Exception('Can only call Property.__equals__ with a Property instance')
    return (
      self._name == value._name and
      self._model is value._model
    )
  
  def _connect(self, entity=None, name=None, model=None):
    super(Property, self)._connect(entity=entity, name=name, model=model)
    if entity and not hasattr(entity, '_values'):
      setattr(entity, '_values', {})
    if model and self.unique:
      setattr(model, '_by_{}'.format(name), Query(self == QueryParameter))
  
  def validate(self, entity, value):
    self._validate_required(value)
    self._validate_types(value)
  
  def _validate_before_save(self, entity, value):
    self._validate_unique(entity, value)
  
  def _validate_required(self, value):
    if self.required and value == None:
      raise PropertyValidationFailed('Required property was None')
  
  def _validate_types(self, value):
    if value != None and len(self.allowed_types) > 0:
      for allowed_type in self.allowed_types:
        if isinstance(value, allowed_type):
          break
      else:
        raise PropertyValidationFailed('Property value does not conform to allowed_types')
  
  def _validate_unique(self, entity, value):
    if not self.unique: return
    query = getattr(self._model, '_by_{}'.format(self._name))
    results = query(value)
    
    for result in results:
      if result.key != entity.key:
        raise PropertyValidationFailed('Property {} was not unique when expected'.format(self._name))
  
  def to_search_field(self):
    raise NotImplementedError()
  
  def to_datastore_property(self):
    raise NotImplementedError()
  
  def to_route_parameter(self):
    raise NotImplementedError()
  
  def __get__(self, instance, cls):
    if instance == None:
      # called on a class
      return self
    return self._get_value(instance)

  def __set__(self, instance, value):
    return self._set_value(instance, value)
  
  def _set_value(self, entity, value):
    self.validate(entity, value)
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
  def __init__(self, required=False, choices=None, hidden=False, unique=False):
    super(ChoicesProperty, self).__init__(required=required, hidden=hidden, unique=unique)
    self.choices = choices
  
  def validate(self, entity, value):
    super(ChoicesProperty, self).validate(entity, value)
    self._validate_choices(value)
  
  def _validate_choices(self, value):
    if self.choices == None: return
    if not value in self.choices:
      raise PropertyValidationFailed('Parameter value not found in allowable choices')


class Integer(ChoicesProperty):
  allowed_operators = PropertyComparison.allowed_operators
  allowed_types = frozenset({int})
  
  def __init__(self, required=False, choices=None, min=None, max=None, hidden=False, unique=False):
    super(Integer, self).__init__(required=required, choices=choices, hidden=hidden, unique=unique)
    self.min = min
    self.max = max
    
  def _from_storage(self, value):
    if value == None:
      return None
    return int(value)
    
  def validate(self, entity, value):
    super(Integer, self).validate(entity, value)
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
  
  def to_route_parameter(self):
    return Parameters.Integer(
      required = self.required,
      choices = self.choices,
      min = self.min,
      max = self.max
    )
    

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
  
  def to_route_parameter(self):
    return Parameters.Float(
      required = self.required,
      choices = self.choices,
      min = self.min,
      max = self.max
    )


class String(ChoicesProperty):
  allowed_operators = PropertyComparison.allowed_operators
  allowed_types = [str, unicode]
  
  def __init__(self, required=False, choices=None, min=None, max=500, characters=None, hidden=False, unique=False):
    super(String, self).__init__(required=required, choices=choices, hidden=hidden, unique=unique)
    self.min = min
    self.max = max
    self.characters = characters
  
  def _to_storage(self, value):
    if value == None:
      return value
    return str(value)
  
  def _from_storage(self, value):
    if value == None:
      return value
    return str(value)
  
  def validate(self, entity, value):
    super(String, self).validate(entity, value)
    if value == None: return
    self._validate_min(value)
    self._validate_max(value)
    self._validate_characters(value)

  def _validate_min(self, value):
    if self.min == None: return
    if len(value) < self.min:
      raise PropertyValidationFailed('StringProperty value length was less than min')
  
  def _validate_max(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise PropertyValidationFailed('StringProperty value length was greater than max')
  
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
  
  def to_route_parameter(self):
    return Parameters.String(
      required = self.required,
      choices = self.choices,
      min = self.min,
      max = self.max,
      characters = self.characters
    )


class UUID(String):
  allowed_operators = frozenset({
    PropertyComparison.EQ
  })
  
  def __init__(self, required=False, hidden=False):
    super(UUID, self).__init__(required=required, hidden=hidden)
  
  def _connect(self, entity=None, name=None, model=None):
    super(String, self)._connect(entity=entity, name=name, model=model)
    if entity:
      import uuid
      token = str(uuid.uuid1())
      self._set_value(entity, token)
    

class Password(String):
  allowed_operators = frozenset({
    PropertyComparison.EQ
  })
  
  def __init__(self, required=False, choices=None, min=None, max=500, characters=None, unique=False):
    super(Password, self).__init__(required=required, choices=choices, min=min, max=max, characters=characters, hidden=True, unique=unique)
  
  def _hash(self, value):
    if value == None: return value
    import hashlib
    return hashlib.sha256(value).hexdigest()
  
  def _set_value(self, entity, value):
    self.validate(entity, value)
    entity._values[self._name] = self._hash(value)

  def _get_stored_value(self, entity):
    return self._get_value(entity)

  def _to_storage(self, value):
    return self._hash(value)


class Model(Property):
  allowed_operators = frozenset({
    PropertyComparison.EQ
  })
  
  def __init__(self, model, required=False, hidden=False, unique=False):
    super(Model, self).__init__(required=required, hidden=hidden, unique=unique)
    self.model = model

  def _get_value(self, entity):
    value = super(Model, self)._get_value(entity)
    if value and not isinstance(value, self.model):
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
  
  def to_route_parameter(self):
    return Parameters.Model(self.model, required = self.required)
