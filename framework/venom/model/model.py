__all__ = ['Model', 'ModelAttribute', 'Model']


class ModelAttribute(object):
  def __init__(self):
    super(ModelAttribute, self).__init__()
    self._model = None
    self._name = None
    self._entity = None
  
  def _fix_up(self, entity=None, name=None, model=None):
    if entity:
      self._entity = entity
      self._model = entity.__class__
    if name:
      self._name = name
    if model:
      self._model = model
  
  @classmethod
  def fix_up(cls, obj, entity=None, model=None):
    for key in dir(obj):
      value = getattr(obj, key)
      if isinstance(value, cls):
        value._fix_up(entity=entity, model=model, name=key)


class MetaModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaModel, cls).__init__(name, bases, classdict)
    ModelAttribute.fix_up(cls, model=cls)


class Model(object):
  __metaclass__ = MetaModel
  
  def __init__(self):
    super(Model, self).__init__()
    ModelAttribute.fix_up(self, entity=self)
    
