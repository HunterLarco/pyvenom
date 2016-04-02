# app engine imports
from google.appengine.ext import ndb


__all__ = ['MetaModel', 'Model']


class MetaModel(ndb.Model.__metaclass__):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    cls._build_helpers()


class Model(ndb.Model):
  __metaclass__ = MetaModel
  
  def __init__(cls, *args, **kwargs):
    super(Model, cls).__init__(*args, **kwargs)
  
  @classmethod
  def _build_helpers(cls):
    for key in set(dir(cls)):
      value = getattr(cls, key, None)
      cls._build_helper(key, value)
  
  @classmethod
  def _build_helper(cls, key, value):
    # based on ndb.Model implementation no properties may begin
    # with an underscore except internal properties so we ignore it
    if key.startswith('_'): return
    # only works in indexed properties
    if isinstance(value, ndb.Property) and value._indexed:
      getKey   = 'getBy{}'  .format(key.capitalize())
      hasKey   = 'hasBy{}'  .format(key.capitalize())
      queryKey = 'queryBy{}'.format(key.capitalize())
      query = lambda cls, val: cls.query(value == val)
      get   = lambda cls, val: cls.query(value == val).get()
      has   = lambda cls, val: cls.query(value == val).count() != 0
      setattr(cls, queryKey, classmethod(query))
      setattr(cls, getKey  , classmethod(get))
      setattr(cls, hasKey  , classmethod(has))