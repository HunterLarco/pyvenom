# system imports
from copy import deepcopy

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
        value._code_name = key
        cls._properties[key] = value
  
  @classmethod
  def _setup_queries(cls):
    cls._queries = QueryDict()
    for key in dir(cls):
      value = getattr(cls, key)
      if isinstance(value, Query):
        cls._queries[key] = value
  
  def __init__(self, **kwargs):
    self.populate(**kwargs)
  
  def populate(self, **kwargs):
    pass
  
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
    
