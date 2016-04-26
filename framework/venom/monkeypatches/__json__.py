from json import JSONEncoder
import datetime
import time

def _default(self, obj):
  if isinstance(obj, datetime.datetime):
    timestamp = time.mktime(obj.timetuple())
    return timestamp
  if hasattr(obj, '__json__'):
    return getattr(obj, '__json__')()
  return obj

_default.default = JSONEncoder().default# Save unmodified default.
JSONEncoder.default = _default# replacement