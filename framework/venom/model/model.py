# package imports
from ..internal.hybrid_model import HybridModel
from attribute import ModelAttribute
from Properties import Property
from query import Query


__all__ = ['Model', 'Model']


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
    from Properties import Property
    cls.kind = cls.__name__
    cls.hybrid_model = type(cls.kind, (HybridModel,), {})
    cls._properties = ModelAttribute.connect(cls, kind=Property)
    cls._queries = ModelAttribute.connect(cls, kind=Query)
  
  def __init__(self, **kwargs):
    super(Model, self).__init__()
    self.hybrid_entity = self.hybrid_model()
    self._connect_properties()
    self._connect_queries()
    self.populate(**kwargs)
  
  def _connect_properties(self):
    for _, prop in self._properties.items():
      prop._connect(entity=self)
  
  def _connect_queries(self):
    for _, query in self._queries.items():
      query._connect(entity=self)
  
  @classmethod
  def _execute_datastore_query(cls, query):
    return cls._execute_query(cls.hybrid_model.query_by_datastore(query))
  
  @classmethod
  def _execute_search_query(cls, query):
    return cls._execute_query(cls.hybrid_model.query_by_search(query))
  
  @classmethod
  def _execute_query(cls, results):
    entities = map(cls._entity_to_model, results)
    return entities
  
  @classmethod
  def _entity_to_model(cls, ndb_entity):
    properties = {name: prop._get_value(ndb_entity) for name, prop in ndb_entity._properties.items()}
    entity = cls()
    entity._populate_from_stored(**properties)
    entity._set_key(ndb_entity.key)
    return entity
  
  def populate(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._properties:
        setattr(self, key, value)
  
  def _populate_from_stored(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._properties:
        prop = self._properties[key]
        prop._set_stored_value(self, value)
  
  def _set_key(self, key):
    self.hybrid_entity.key = key
    self.hybrid_entity.document_id = key.pairs()[0][1]
  
  def put(self):
    for key, prop in self._properties.items():
      value = prop._get_stored_value(self)
      if prop.search:
        for field in prop.search_fields:
          self.hybrid_entity.set(key, value, field)
      property = prop.to_datastore_property()
      self.hybrid_entity.set(key, value, property)
    self.hybrid_entity.put()
