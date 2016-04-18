from google.appengine.ext import ndb
from google.appengine.api import search


__all__ = ['DynamicModel', 'HybridModel', 'MetaHybridModel']


class DynamicModel(ndb.Model):
  def __getattr__(self, name):
    if name in self._properties:
      return self._properties[name]._get_value(self)
    cls = self.__class__
    raise AttributeError("'{}' object has no attribute '{}'".format(cls.__name__, name))
  
  def __setattr__(self, name, value):
    if name in self._properties:
      return self._properties[name]._set_value(self, value)
    return super(DynamicModel, self).__setattr__(name, value)
  
  def __delattr__(self, name):
    if name in self._properties:
      del self._properties[name]
      return None
    return super(DynamicModel, self).__delattr__(name)
  
  def set(self, name, value, property):
    self._clone_properties()
    if isinstance(property, ndb.Property):
      prop = property
    elif issubclass(property, ndb.Property):
      prop = property()
    else:
      raise Exception('Unknown property {}'.format(property))
    prop._name = name
    prop._code_name = name
    self._properties[name] = prop
    prop._set_value(self, value)


class MetaHybridModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaHybridModel, cls).__init__(name, bases, classdict)
    cls._init_class()


class HybridModel(object):
  __metaclass__ = MetaHybridModel
  
  # attributes updates by metaclass
  kind = None
  model = None
  index = None
  
  @classmethod
  def _init_class(cls):
    cls.kind = cls.__name__
    cls.model = type(cls.kind, (DynamicModel,), {})
    cls.index = search.Index(name=cls.kind)
  
  def __init__(self, key=None, document_id=None):
    super(HybridModel, self).__init__()
    self._search_properties = {}
    self._datastore_properties = {}
    self.key = None
    if key:
      self.key = key
      self.document_id = key.pairs()[0][1]
    if document_id:
      self.key = ndb.Key(self.kind, document_id)
      self.document_id = document_id
  
  def set(self, name, value, property):
    if isinstance(property, ndb.Property):
      self._set_datastore_property(name, value, property)
    elif issubclass(property, ndb.Property):
      self._set_datastore_property(name, value, property())
    elif issubclass(property, search.Field):
      self._set_search_property(name, value, property)
    else:
      raise Exception('Unknown property {}'.format(property))
  
  def _set_datastore_property(self, name, value, property_instance):
    self._datastore_properties[name] = (value, property_instance)
  
  def _set_search_property(self, name, value, field_class):
    field = field_class(name=name, value=value)
    self._search_properties[name] = field
  
  def _to_search_document(self):
    return search.Document(fields = self._search_properties.values())
  
  def _to_datastore_entity(self, key=None):
    entity = self.model()
    for name, (value, prop) in self._datastore_properties.items():
      entity.set(name, value, prop)
    if key:
      entity.key = entity._key = key
    return entity
  
  def put(self):
    if self.key:
      return self._put_update()
    return self._put_new()
  
  def _put_new(self):
    document = self._to_search_document()
    results = self.index.put(document)
    document_id = results[0].id
    entity_key = ndb.Key(self.kind, document_id)
    entity = self._to_datastore_entity(key=entity_key)
    entity.put()
    # update current key and document_id
    # since they do not exist
    self.key = entity_key
    self.document_id = document_id
    return entity
  
  def _put_update(self):
    document = self.index.get(self.document_id)
    fields = document.fields
    search_properties = { key: value for key, value in self._search_properties.items() }
    for field in fields:
      if not field.name in search_properties:
        search_properties[field.name] = field
    document = search.Document(fields=search_properties.values(), doc_id=self.document_id)
    self.index.put(document)
    
    entity = self.key.get()
    for key, (value, prop) in self._datastore_properties.items():
      if not hasattr(entity, key):
        entity.set(key, value, prop)
      else:
        setattr(entity, key, value)
    entity.put()
  
  @classmethod
  def query_by_search(self, query_string):
    options = search.QueryOptions(ids_only=True)
    query = search.Query(query_string, options=options)
    documents = self.index.search(query)
    keys = [ndb.Key(self.kind, document.doc_id) for document in documents]
    entities = ndb.get_multi(keys)
    return entities
  
  @classmethod
  def query_by_datastore(self, query_component=None):
    query = self.model.query(query_component) if query_component else self.model.query()
    entities = list(query)
    return entities
  
  def delete(self):
    self.index.delete(self.document_id)
    self.key.delete()
