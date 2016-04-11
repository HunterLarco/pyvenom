# system imports
import copy

# application imports
import Properties
from query import Query, QueryDict
from internal.hybrid import HybridModel


__all__ = ['Model']


class MetaModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    cls._setup_properties()
    cls._setup_queries()


class Model(object):
  __metaclass__ = MetaModel
  
  @classmethod
  def _setup_properties(cls):
    cls._properties = {}
    for key in dir(cls):
      value = getattr(cls, key)
      if isinstance(value, Properties.Property):
        value._name = key
        cls._properties[key] = value
  
  @classmethod
  def _setup_queries(cls):
    cls._queries = QueryDict()
    for key in dir(cls):
      value = getattr(cls, key)
      if isinstance(value, Query):
        cls._queries[key] = value
        value._model = cls
  
  @classmethod
  def _query_by_search(cls, query):
    hybrid = HybridModel(cls.__name__)
    entities = hybrid.query_by_search(query.to_query_string())
    for i, entity in enumerate(entities):
      prop_values = {}
      for prop_name, ndb_prop in entity._properties.items():
        if prop_name in cls._properties:
          prop_values[prop_name] = ndb_prop._get_value(entity)
      entities[i] = cls(**prop_values)
    return entities
  
  def __init__(self, **kwargs):
    self._values = {}
    self.populate(**kwargs)
  
  def populate(self, **kwargs):
    for key, value in kwargs.items():
      if key in self._properties:
        setattr(self, key, value)
  
  def save(self):
    hybrid = HybridModel(self.__class__.__name__)
    for key, prop in self._properties.items():
      hybrid.property(key, prop.to_ndb_property(), prop._value)
    
    search_properties = self._queries.get_search_properties()
    # invert the properties dictionary
    property_to_name = {v: k for k, v in self._properties.items()}
    for prop in search_properties:
      name = property_to_name[prop]
      hybrid.property(name, prop.to_search_field(), prop._value)
    
    hybrid.put()
  
  @classmethod
  def get(cls, identifier):
    pass
  
  def __repr__(self):
    props = []
    for prop_name, prop in self._properties.items():
      props.append('{}={}'.format(prop_name, prop.__get__(self, self.__class__)))
    return '{}({})'.format(self.__class__.__name__, ', '.join(props))
    
