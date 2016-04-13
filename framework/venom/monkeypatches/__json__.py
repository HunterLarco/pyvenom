from json import JSONEncoder

def _default(self, obj):
  if hasattr(obj, '__json__'):
    return getattr(obj, '__json__')()
  return obj

_default.default = JSONEncoder().default# Save unmodified default.
JSONEncoder.default = _default# replacement