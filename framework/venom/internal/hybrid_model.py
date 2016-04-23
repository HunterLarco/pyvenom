# system imports
from collections import namedtuple

# app engine imports
from google.appengine.ext import ndb
from google.appengine.api import search
from google.net.proto.ProtocolBuffer import ProtocolBufferDecodeError


__all__ = ['DynamicModel', 'HybridModel', 'MetaHybridModel', 'HybridSearchDocument', 'HybridDatastoreEntity', 'HybridPutManager']


# TODO try this when the key of it yields nothing from the db


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


class HybridSearchDocument(object):
  def __init__(self, index, document=None, document_id=None):
    if document_id and document and not document.doc_id:
      document._doc_id = document_id
    
    self.index = index
    self._set_document(document)
    if document_id: self.document_id = document_id
  
  def has_diff(self, fields):
    document = self.get_document()
    if not document: return len(fields) != 0
    provided_fields = { field.name: field for field in fields }
    document_fields = { field.name: field for field in document.fields }
    if provided_fields.keys() != document_fields.keys(): return True
    for key, provided_field in provided_fields.items():
      document_field = document_fields[key]
      if not document_field.value == provided_field.value: return True
    return False
  
  def get_update_document(self, fields):
    if not self.document_id:
      # must be a new entry
      return search.Document(fields=fields)
    return search.Document(fields=fields, doc_id=self.document_id)
  
  def get_document(self):
    if self._loaded_document:
      return self.document
    elif self.document_id:
      self.document = self.index.get(self.document_id)
      self._loaded_document = True
      return self.document
    return None
  
  def register_update(self, document, put_result):
    document._doc_id = put_result.id
    self._set_document(document)
  
  def _set_document(self, document):
    self.document = document
    self.document_id = document.doc_id if document and document.doc_id else None
    self._loaded_document = bool(document)


DatastorePropertyContainer = namedtuple('DatastorePropertyContainer', 'property name value')

class HybridDatastoreEntity(object):
  def __init__(self, dynamic_model, entity=None, entity_key=None):
    if entity_key and entity and not entity.key:
      entity._key = entity.key = entity_key
    
    self.dynamic_model = dynamic_model
    self._set_entity(entity)
    if entity_key: self.entity_key = entity_key
  
  def has_diff(self, properties):
    entity = self.get_entity()
    if not entity: return True
    provided_properties = [ prop.name for prop in properties ]
    entity_properties = entity._properties
    if provided_properties != entity_properties.keys(): return True
    for ndb_prop, prop_name, provided_value in properties:
      entity_value = getattr(entity, prop_name)
      if not provided_value == entity_value: return True
    return False
  
  def get_update_entity(self, properties):
    entity = self.dynamic_model()
    for ndb_prop, name, value in properties:
      entity.set(name, value, ndb_prop)
    if self.entity_key:
      # entity is updating, not writing for the first time
      entity.key = entity._key = self.entity_key
    return entity
  
  def get_entity(self):
    if self._loaded_entity:
      return self.entity
    elif self.entity_key:
      if hasattr(self.entity_key, 'get'):
        self.entity = self.entity_key.get()
      self._loaded_entity = True
      return self.entity
    return None
  
  def register_update(self, entity):
    self._set_entity(entity)
  
  def _set_entity(self, entity):
    self.entity = entity
    self.entity_key = entity.key if entity else None
    self._loaded_entity = bool(entity)


class HybridPutManager(object):
  maximum_search_put = 200
  
  def __init__(self, hybrid_entities):
    self.hybrids = []
    
    if not isinstance(hybrid_entities, list):
      hybrid_entities = [hybrid_entities]
    for hybrid_entity in hybrid_entities:
      self.add(hybrid_entity)
  
  def add(self, hybrid_entity):
    self.hybrids.append(hybrid_entity)
  
  def _put_search_documents(self):
    search_indexes = {}
    for hybrid in self.hybrids:
      if hybrid.document_has_diff():
        document = hybrid.get_update_document()
        if not hybrid.kind in search_indexes:
          search_indexes[hybrid.kind] = {
            'index': hybrid.index,
            'documents': [],
            'hybrids': []
          }
        search_indexes[hybrid.kind]['documents'].append(document)
        search_indexes[hybrid.kind]['hybrids'].append(hybrid)
    
    for search_info in search_indexes.values():
      index = search_info['index']
      documents = search_info['documents']
      hybrids = search_info['hybrids']
      results = []
      for i in range(0, len(documents), self.maximum_search_put):
        results += index.put(documents[i: i + self.maximum_search_put])
      
      for hybrid, document, result in zip(hybrids, documents, results):
        hybrid.register_document(document, result)
  
  def _put_datastore_entities(self):
    entities = []
    saved_hybrids = []
    for hybrid in self.hybrids:
      if hybrid.datastore_has_diff():
        entities.append(hybrid.get_update_entity())
        saved_hybrids.append(hybrid)
    
    ndb.put_multi(entities)
    
    for entity, hybrid in zip(entities, saved_hybrids):
      hybrid.register_entity(entity)
  
  def get_results(self):
    self._put_datastore_entities()
    self._put_search_documents()


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
  
  # constants
  default_indexed = False
  
  @classmethod
  def _init_class(cls):
    cls.kind = cls.__name__
    cls.model = type(cls.kind, (DynamicModel,), {})
    cls.index = search.Index(name=cls.kind)
  
  def __init__(self, entity=None, document=None):
    super(HybridModel, self).__init__()
    self._search_properties = {}
    self._datastore_properties = {}
    
    document_id = None
    if entity and entity.key:
      document_id = self._key_to_document_id(entity.key)
    
    entity_key = None
    if document and hasattr(document, 'doc_id'):
      entity_key = self._document_id_to_key(document.doc_id)
    
    self.search_document = HybridSearchDocument(self.index, document=document, document_id=document_id)
    self.datastore_entity = HybridDatastoreEntity(self.model, entity=entity, entity_key=entity_key)

  @property
  def entity_key(self):
    if self.search_document.document_id:
      return self._document_id_to_key(self.search_document.document_id)
    elif self.datastore_entity.entity_key:
      return self.datastore_entity.entity_key
    return None
    
  @property
  def document_id(self):
    if self.search_document.document_id:
      return self.search_document.document_id
    elif self.datastore_entity.entity_key:
      return self._key_to_document_id(self.datastore_entity.entity_key)
    return None

  def _get_document_fields(self):
    return self._search_properties.values()

  def document_has_diff(self):
    fields = self._get_document_fields()
    return self.search_document.has_diff(fields)
  
  def get_update_document(self):
    fields = self._get_document_fields()
    if not self.search_document.get_document():
      entity_key = self.datastore_entity.entity_key
      if entity_key:
        document_id = self._key_to_document_id(entity_key)
        self.search_document.document_id = document_id
        self.search_document._loaded_document = False
    return self.search_document.get_update_document(fields)
  
  def register_document(self, document, result):
    return self.search_document.register_update(document, result)
  
  def _get_datastore_properties(self):
    return [
      DatastorePropertyContainer(property, name, value)
      for name, (value, property) in self._datastore_properties.items()
    ]

  def datastore_has_diff(self):
    properties = self._get_datastore_properties()
    return self.datastore_entity.has_diff(properties)
  
  def get_update_entity(self):
    properties = self._get_datastore_properties()
    return self.datastore_entity.get_update_entity(properties)
  
  def register_entity(self, entity):
    return self.datastore_entity.register_update(entity)

  def set(self, name, value, property):
    if isinstance(property, ndb.Property):
      self._set_datastore_property(name, value, property)
    elif issubclass(property, ndb.Property):
      self._set_datastore_property(name, value, property(indexed=self.default_indexed))
    elif issubclass(property, search.Field):
      self._set_search_property(name, value, property)
    else:
      raise Exception('Unknown property {}'.format(property))
  
  def _set_datastore_property(self, name, value, property_instance):
    self._datastore_properties[name] = (value, property_instance)
  
  def _set_search_property(self, name, value, field_class):
    field = field_class(name=name, value=value)
    self._search_properties[name] = field
  
  def delete(self):
    self.index.delete(self.document_id)
    self.entity_key.delete()
  
  def put(self):
    self.put_multi([self])
  
  @classmethod
  def put_multi(cls, hybrid_entities):
    HybridPutManager(hybrid_entities).get_results()
  
  @classmethod
  def get(cls, entity_key_or_document_id):
    return cls.get_multi([entity_key_or_document_id])[0]
  
  @classmethod
  def get_multi(cls, entity_keys_or_document_ids):
    to_grab = [
      entity_key_or_document_id if isinstance(entity_key_or_document_id, ndb.Key)
      else cls._document_id_to_key(entity_key_or_document_id)
      for entity_key_or_document_id in entity_keys_or_document_ids
    ]
    grabbed = ndb.get_multi(to_grab)
    return [
      cls(entity=entity) if entity
      else None
      for entity in grabbed
    ]

  @classmethod
  def query_by_search(cls, query_string):
    options = search.QueryOptions(ids_only=True)
    query = search.Query(query_string, options=options)
    documents = cls.index.search(query)
    keys = [cls._document_id_to_key(document.doc_id) for document in documents]
    entities = ndb.get_multi(keys)
    return [ cls(entity=datastore_entity) for datastore_entity in entities ]
  
  @classmethod
  def query_by_datastore(cls, query_component=None):
    query = cls.model.query(query_component) if query_component else cls.model.query()
    return [ cls(entity=datastore_entity) for datastore_entity in query ]
  
  @classmethod
  def _key_to_document_id(cls, key):
    return str(key.id())
  
  @classmethod
  def _document_id_to_key(cls, document_id):
    try:
      return ndb.Key(cls.kind, int(document_id))
    except ValueError:
      return ndb.Key(cls.kind, 'no_entity')
