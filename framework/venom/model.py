# system imports
from copy import deepcopy

# application imports
import Properties


__all__ = ['Model']


class MetaModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    cls._connect_properties_to_model()


class Model(object):
  __metaclass__ = MetaModel
  
  @classmethod
  def _connect_properties_to_model(cls):
    cls._properties = {}
    for key in set(dir(cls)):
      value = getattr(cls, key, None)
      cls._connect_property(key, value)
  
  @classmethod
  def _connect_property(cls, key, value):
    if isinstance(value, Properties.Property):
      cls._properties[key] = value
      value._connect_to_model(key, cls)
  
  def __init__(self, **kwargs):
    self._clear_properties()
    self._connect_properties_to_instance()
    self.populate(**kwargs)
  
  def _clear_properties(self):
    for key, prop in self._properties.items():
      setattr(self, key, None)

  def _connect_properties_to_instance(self):
    for key, prop in self._properties.items():
      self._properties[key] = deepcopy(prop)
      self._properties[key]._connect_to_instance(self)
  
  def enforce(self):
    for key, prop in self._properties.items():
      prop.enforce()
  
  def populate(self, **kwargs):
    pass
    
