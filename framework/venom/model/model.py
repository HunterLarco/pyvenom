# system imports
import inspect

# package imports
from ..internal.hybrid_model import HybridModel


__all__ = ['Model', 'ModelAttribute', 'Model']


class ModelAttribute(object):
  _model = None
  _name = None
  _entity = None
  
  def _connect(self, entity=None, name=None, model=None):
    if entity:
      self._entity = entity
      self._model = entity.__class__
    if name:
      self._name = name
    if model:
      self._model = model
  
  @classmethod
  def connect(cls, obj):
    results = {}
    model, entity = (obj, None) if inspect.isclass(obj) else (None, obj)
    for key in dir(obj):
      value = getattr(obj, key)
      if isinstance(value, cls):
        value._connect(entity=entity, model=model, name=key)
        results[key] = value
    return results


class MetaModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    cls._init_class()


class Model(object):
  __metaclass__ = MetaModel
  
  # attributes updates by metaclass
  kind = None
  hybrid_model = None
  
  @classmethod
  def _init_class(cls):
    cls.kind = cls.__name__
    cls.hybrid_model = type(cls.kind, (HybridModel,), {})
    cls._properties = ModelAttribute.connect(cls)
  
  def __init__(self, **kwargs):
    super(Model, self).__init__()
    self.hybrid_entity = self.hybrid_model()
    self._connect_properties()
    self.populate(**kwargs)
  
  def _connect_properties(self):
    for _, prop in self._properties.items():
      prop._connect(entity=self)
  
  def _execute_datastore_query(self, query):
    return []
  
  def _execute_search_query(self, query):
    return []
  
  def populate(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._properties:
        setattr(self, key, value)
  
  def _populate_from_stored(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._properties:
        prop = self._properties[key]
        prop._set_stored_value(self, value)
  
  def put(self):
    for key, prop in self._properties.items():
      value = prop._get_stored_value(self)
      if prop.search:
        for field in prop.search_fields:
          self.hybrid_entity.set(key, value, field)
      if prop.datastore:
        for property in prop.datastore_properties:
          self.hybrid_entity.set(key, value, property)
    self.hybrid_entity.put()
