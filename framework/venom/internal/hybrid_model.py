from google.appengine.ext import ndb
from google.appengine.api import search


__all__ = ['DynamicModel']


class DynamicModel(ndb.Model):
  _default_indexed = False
  
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



