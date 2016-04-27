# system imports
import inspect


__all__ = ['ModelAttribute']


class ModelAttribute(object):
  _model = None
  _name = None
  _entity = None
  
  def _connect(self, entity=None, name=None, model=None):
    if entity:
      self._entity = entity
      self._model = entity.__class__
    if name:
      self._name = name
    if model:
      self._model = model
  
  @classmethod
  def connect(cls, obj, kind=None):
    results = {}
    model, entity = (obj, None) if inspect.isclass(obj) else (None, obj)
    for key in dir(obj):
      value = getattr(obj, key)
      if isinstance(value, cls):
        if kind and not isinstance(value, kind):
          continue
        value._connect(entity=entity, model=model, name=key)
        results[key] = value
    return results