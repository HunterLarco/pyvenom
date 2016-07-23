# PSL imports
import inspect


__all__ = [
  'Exporter'
]


class Exporter(object):
  def __init__(self, __all__):
    super(Exporter, self).__init__()
    self.__all__ = __all__
  
  def __call__(self, *args):
    if len(args) == 1 and (
        inspect.isfunction(args[0])
        or inspect.isclass(args[0])):
      return self._decorator(*args)
    return self._function(*args)
  
  def _decorator(self, funct_or_cls):
    name = funct_or_cls.__name__
    self.__all__.append(name)
    return funct_or_cls
  
  def _function(self, *exports):
    for export in exports:
      if not isinstance(export, str):
        raise ValueError('Exporter can only export variables by name (type str)')
    self.__all__.extend(exports)
  
  def __repr__(self):
    return 'Exporter()'
