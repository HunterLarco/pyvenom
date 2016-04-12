# system imports
import json


class DunderJSONEncoder(json.JSONEncoder):
  def default(self, obj):
    if hasattr(obj, '__json__'):
      return getattr(obj, '__json__')()
    return obj


def loads(*args, **kwargs):
  return json.loads(*args, **kwargs)

def dumps(*args, **kwargs):
  kwargs['cls'] = DunderJSONEncoder
  return json.dumps(*args, **kwargs)