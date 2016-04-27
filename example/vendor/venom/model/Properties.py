# system imports
import datetime
import time

# app engine imports
from google.appengine.ext import ndb
from google.appengine.api import search

# package imports
from attribute import ModelAttribute
from query import PropertyComparison, Query, QueryParameter
from ..routing import Parameters


__all__  = [
  'Property', 'ChoicesProperty', 'Integer', 'Float', 'String',
  'Password', 'UUID', 'Model',
  'InvalidPropertyComparison', 'PropertyValidationFailed'
]


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
    self._code_name = 'Property'
  
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
    if name and self._model:
      self._code_name = '{}.{}'.format(self._model.kind, name)
  
  def validate(self, entity, value):
    self._validate_required(value)
    self._validate_types(value)
  
  def _validate_before_save(self, entity, value):
    self._validate_unique(entity, value)
  
  def _validate_required(self, value):
    if self.required and value == None:
      raise PropertyValidationFailed(
        "'{}' property was set to None, but is required"
        .format(self._code_name)
      )
  
  def _validate_types(self, value):
    if value != None and len(self.allowed_types) > 0:
      for allowed_type in self.allowed_types:
        if isinstance(value, allowed_type):
          break
      else:
        raise PropertyValidationFailed(
          "{} property was set to {} of type '{}' when the only allowed types are {}"
          .format(
            self._code_name, value,
            type(value).__name__,
            map(lambda typ: typ.__name__, self.allowed_types)
          )
        )
  
  def _validate_unique(self, entity, value):
    if not self.unique: return
    query = getattr(self._model, '_by_{}'.format(self._name))
    results = query(value)
    
    for result in results:
      if result.key != entity.key:
        raise PropertyValidationFailed(
          '{0} most contain a unique value but another entity already contains {0} == {1!r}'
          .format(self._code_name, value)
        )
  
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
      raise PropertyValidationFailed(
        "'{}' field must be one of {} but instead it was '{}'"
        .format(self._code_name, self.choices, value)
      )


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
      raise PropertyValidationFailed(
        "{} property must be at least {} but was {}"
        .format(self._code_name, self.min, value)
      )
  
  def _validate_max(self, value):
    if self.max == None: return
    if value > self.max:
      raise PropertyValidationFailed(
        "{} property must be at most {} but was {}"
        .format(self._code_name, self.max, value)
      )
    
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
      raise PropertyValidationFailed(
        "{} property requires at least {} characters but was provided '{}' of length {}"
        .format(self._code_name, self.min, value, len(value))
      )
  
  def _validate_max(self, value):
    if self.max == None: return
    if len(value) > self.max:
      raise PropertyValidationFailed(
        "{} property requires at most {} characters but was provided '{}' of length {}"
        .format(self._code_name, self.max, value, len(value))
      )
  
  def _validate_characters(self, value):
    if self.characters == None: return
    difference = set(value) - set(self.characters)
    if len(difference) > 0:
      raise PropertyValidationFailed(
        "{} property can only contain characters from '{}' but found characters from '{}'"
        .format(self._code_name, ''.join(self.characters), ''.join(difference))
      )

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
    entity._values[self._name] = value
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


class DateTime(Float):
  allowed_types = frozenset({datetime.datetime})
  
  def __init__(self, required=False, choices=None, min=None, max=None, hidden=False, unique=False, set_on_creation=False, set_on_update=False):
    super(Float, self).__init__(required=required, choices=choices, hidden=hidden, unique=unique, min=min, max=max)
    self.set_on_creation = set_on_creation
    self.set_on_update = set_on_update
  
  def _to_storage(self, value):
    if value == None: return None
    timestamp = time.mktime(value.timetuple())
    return super(DateTime, self)._from_storage(timestamp)
  
  def _from_storage(self, value):
    value = super(DateTime, self)._from_storage(value)
    if value == None: return None
    return datetime.datetime.fromtimestamp(value)
  
  def _validate_before_save(self, entity, value):
    super(DateTime, self)._validate_before_save(entity, value)
    
    if self.set_on_creation and not entity.key:
      self._set_value(entity, datetime.datetime.now())
    
    if self.set_on_update:
      self._set_value(entity, datetime.datetime.now())
