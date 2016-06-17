__all__ = [
  # Exceptions
  'InvalidEnumType',
  # Main Classes
  'Enum', 'EnumValue'
]


class InvalidEnumType(Exception):
  pass


class EnumValue(object):
  def __init__(self, name, enum):
    self.name = name
    self.enum = enum
  
  def __gt__(self, _):
    raise NotImplementedError("Class EnumValue does not support '>' comparison")
  def __ge__(self, _):
    raise NotImplementedError("Class EnumValue does not support '>=' comparison")
  def __lt__(self, _):
    raise NotImplementedError("Class EnumValue does not support '<' comparison")
  def __le__(self, _):
    raise NotImplementedError("Class EnumValue does not support '<=' comparison")
  def contains(self, _):
    raise NotImplementedError("Class EnumValue does not support 'in' comparison")
  
  def __ne__(self, value):
    return not (self == value)
  
  def __eq__(self, value):
    return (self.name == value.name
        and self.enum.name == value.enum.name)
  
  def __hash__(self):
    return hash(repr(self))
  
  def __repr__(self):
    return '<EnumValue {}.{}>'.format(self.enum.name, self.name)


class Enum(object):
  # _values = {}
  # name = ""
  
  def __init__(self, name, iterable):
    super(Enum, self).__init__()
    self._values = {}
    self.name = name
    
    for item in iterable:
      if not type(item) == str:
        raise InvalidEnumType("Enum values must be of type <type 'str'>")
      value = EnumValue(item, self)
      self._values[item] = value
  
  def __getattribute__(self, key):
    _values = object.__getattribute__(self, '_values')
    if key in _values:
      return _values[key]
    return object.__getattribute__(self, key)
  
  def __setattribute__(self, key, _):
    if key in self._values:
      raise NotImplementedError()
  
  def __repr__(self):
    return '<Enum {}>'.format(self.name)
