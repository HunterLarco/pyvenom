# system imports
from collections import defaultdict

# app engine imports
from google.appengine.ext import ndb
from google.appengine.api import search


__all__ = ['DynamicModel', 'HybridModel', 'MetaHybridModel']


# Todo try this when the key of it yields nothing from the db


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


class PutAsync(object):
  def __init__(self, entities):
    if not isinstance(entities, list):
      entities = [entities]
    
    self.datastore = []
    self.search = defaultdict(list)
    self.new_datastore = []
    
    self._has_put = False
    
    for entity in entities:
      self.add(entity)
  
  def add(self, entity):
    if entity.datastore_requires_update():
      if entity.exists_in_datastore():
        self.datastore.append(entity)
      else:
        self.new_datastore.append(entity)
  
    if entity.search_requires_update():
      self.search[entity.index.name].append(entity)
      
  def put(self):
    if self._has_put:
      raise Exception('Cannot reuse PutAsync')
    self._has_put = True
    
    for hybrid_entities in self.search.values():
      if hybrid_entities:
        index = hybrid_entities[0].index
        documents = [
          hybrid_entity.form_search_document()
          for hybrid_entity in hybrid_entities
        ]
        doc_ids = index.put(documents)
        for hybrid_entity, document, doc_id in zip(hybrid_entities, documents, doc_ids):
          document._doc_id = doc_id.id
          hybrid_entity._register_search_document(document)
    
    entities = []
    for hybrid_entity in self.new_datastore:
      ndb_key = ndb.Key(hybrid_entity.kind, hybrid_entity.search_document.doc_id)
      ndb_entity = hybrid_entity.form_datastore_entity(key=ndb_key)
      entities.append(ndb_entity)
    
    for hybrid_entity in self.datastore:
      entities.append(hybrid_entity.form_datastore_entity())
    
    ndb.put_multi(entities)


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
  
  def __init__(self, key=None, document_id=None, entity=None, document=None):
    super(HybridModel, self).__init__()
    self._search_properties = {}
    self._datastore_properties = {}
    
    self.key = None
    self.document_id = None
    
    self.entity = entity
    self._entity_loaded = bool(entity)
    self.document = document
    self._document_loaded = bool(document)
    
    if document:
      self.key = ndb.Key(self.kind, document.doc_id)
      self.document_id = document.doc_id
    elif entity:
      self.key = entity.key
      self.document_id = self.key.pairs()[0][1]
    elif key:
      self.key = key
      self.document_id = key.pairs()[0][1]
    elif document_id:
      self.key = ndb.Key(self.kind, document_id)
      self.document_id = document_id
  
  def datastore_requires_update(self):
    entity = self.datastore_entity
    if not entity:
      return True
    for key, (prop_value, prop) in self._datastore_properties.items():
      if not hasattr(entity, key):
        return True
      entity_value = getattr(entity, key)
      if not entity_value == prop_value:
        return True
    return False
  
  def search_requires_update(self):
    document = self.search_document
    if not document:
      return True
    fields = {
      field.name: field
      for field in document.fields
    }
    if set(fields.keys()) != set(self._search_properties.keys()):
      return True
    for key, prop in self._search_properties.items():
      field_value = fields[key].value
      if not field_value == prop.value:
        return True
    return False
  
  def exists_in_datastore(self):
    return bool(self.datastore_entity)
  
  def exists_in_search(self):
    return bool(self.search_document)
  
  @property
  def datastore_entity(self):
    if not self.key:
      return None
    if not self._entity_loaded:
      self.entity = self.key.get()
      self._entity_loaded = True
    return self.entity
  
  @property
  def search_document(self):
    if not self.document_id:
      return None
    if not self._document_loaded:
      self.document = self.index.get(self.document_id)
      self._document_loaded = True
    return self.document
  
  def _register_search_document(self, document):
    self.document = document
    self.document_id = document.doc_id if document else None
  
  def _register_datastore_entity(self, entity):
    self.entity = entity
    self.key = entity.key if entity else None
  
  def form_search_document(self):
    if not self.exists_in_search():
      return search.Document(fields = self._search_properties.values())
    document = self.search_document
    fields = document.fields
    search_properties = { key: value for key, value in self._search_properties.items() }
    for field in fields:
      if not field.name in search_properties:
        search_properties[field.name] = field
    return search.Document(fields=search_properties.values(), doc_id=self.document_id)
  
  def form_datastore_entity(self, key=None):
    if not self.exists_in_datastore():
      entity = self.model()
      for name, (value, prop) in self._datastore_properties.items():
        entity.set(name, value, prop)
      if key:
        entity.key = entity._key = key
      return entity
    entity = self.datastore_entity
    for key, (value, prop) in self._datastore_properties.items():
      if not hasattr(entity, key):
        entity.set(key, value, prop)
      else:
        setattr(entity, key, value)
    return entity
  
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
  
  def put(self):
    PutAsync(self).put()

  def _has_search_diff(self, document):
    fields = {
      field.name: field
      for field in document.fields
    }
    if set(fields.keys()) != set(self._search_properties.keys()):
      return True
    for key, prop in self._search_properties.items():
      field_value = fields[key].value
      if not field_value == prop.value:
        return True
    return False
  
  def _has_datastore_diff(self, entity):
    for key, (prop_value, prop) in self._datastore_properties.items():
      if not hasattr(entity, key):
        return True
      entity_value = getattr(entity, key)
      if not entity_value == prop_value:
        return True
    return False

  @classmethod
  def query_by_search(self, query_string):
    options = search.QueryOptions(ids_only=True)
    query = search.Query(query_string, options=options)
    documents = self.index.search(query)
    keys = [ndb.Key(self.kind, document.doc_id) for document in documents]
    entities = ndb.get_multi(keys)
    hybrid_entities = map(self.entity_to_hybrid_entity, entities)
    return hybrid_entities
  
  @classmethod
  def query_by_datastore(self, query_component=None):
    query = self.model.query(query_component) if query_component else self.model.query()
    hybrid_entities = map(self.entity_to_hybrid_entity, query)
    return hybrid_entities
  
  @classmethod
  def entity_to_hybrid_entity(cls, entity):
    return cls(entity=entity)
  
  def delete(self):
    self.index.delete(self.document_id)
    self.key.delete()
  
  @classmethod
  def get(cls, key=None, document_id=None):
    if document_id:
      key = ndb.Key(cls.kind, document_id)
    entity = key.get()
    return cls.entity_to_hybrid_entity(entity)
  
  @classmethod
  def get_multi(cls, keys=None, document_ids=None):
    if document_ids:
      keys = map(lambda id: ndb.Key(cls.kind, id), document_ids)
    entities = ndb.get_multi(keys)
    return map(cls.entity_to_hybrid_entity, entities)
  
  @classmethod
  def put_multi(cls, entities):
    PutAsync(entities).put()
