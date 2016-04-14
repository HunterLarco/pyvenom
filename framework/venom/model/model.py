# system imports
import inspect


__all__ = ['Model', 'ModelAttribute', 'Model']


class ModelAttribute(object):
  def __init__(self):
    super(ModelAttribute, self).__init__()
    self._model = None
    self._name = None
    self._entity = None
  
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
    model, entity = (obj, None) if inspect.isclass(obj) else (None, obj)
    for key in dir(obj):
      value = getattr(obj, key)
      if isinstance(value, cls):
        value._connect(entity=entity, model=model, name=key)


class MetaModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    ModelAttribute.connect(cls)


class Model(object):
  __metaclass__ = MetaModel
  
  def __init__(self):
    super(Model, self).__init__()
    ModelAttribute.connect(self)
    
