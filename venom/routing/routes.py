# package imports
import Parameters
import Protocols
from handlers import Servable


__all__  = ['Route', 'Path']
__all__ += ['GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'DELETE', 'OPTIONS', 'TRACE']


class Path(str):
  def matches(self, path):
    desired_path = self._traverse_path(self)
    given_path = self._traverse_path(path)
    
    if len(desired_path) != len(given_path):
      return False
    
    for desired, given in zip(desired_path, given_path):
      if not desired.startswith(':') and desired != given:
        return False
    
    return True
  
  @classmethod
  def _traverse_path(cls, path):
    sanitized_path = cls._sanitize_path(path)
    parts = sanitized_path.split('/')
    return parts 
  
  @staticmethod
  def _sanitize_path(path):
    if path.endswith('/'): path = path[:-1]
    if path.startswith('/'): path = path[1:]
    return path
  
  def has_parameters(self):
    return ':' in self
  
  def get_parameters(self, path):
    desired_path = self._traverse_path(self)
    given_path = self._traverse_path(path)
    
    return {
      desired[1:] : given
      for desired, given in zip(desired_path, given_path)
      if desired.startswith(':')
    }


class Route(object):
  allowed_methods = frozenset((
    'GET', 'POST', 'PUT', 'PATCH',
    'HEAD', 'DELETE', 'OPTIONS', 'TRACE'
  ))
  
  _attributes = ['path']
  
  def __init__(self, path, handler, protocol=Protocols.JSONProtocol):
    super(Route, self).__init__()
    
    if not issubclass(handler, Servable):
      raise Exception('Route handler must be a Servable subclass')
    
    self.path = Path(path)
    self.handler = handler
    self.protocol = protocol
    self._url = Parameters.Dict({})
    self._body = Parameters.Dict({})
    self._query = Parameters.Dict({})
    self._headers = Parameters.Dict({})
  
  def matches_method(self, method):
    return method.upper() in self.allowed_methods
  
  def matches_path(self, path):
    return self.path.matches(path)
  
  def matches(self, path, method):
    return self.matches_path(path) and self.matches_method(method)
  
  def handle(self, request, response, error, errors=None):
    errors = errors if errors else {}
    with self.protocol(request, response, error, errors) as protocol:
      handler = self.handler(request, response, error, self, protocol)
      response = handler.serve()
      protocol._write(response)
  
  def url(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._url = params
    return self
  
  def body(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._body = params
    return self
  
  def query(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._query = params
    return self
  
  def headers(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._headers = params
    return self
  
  def __repr__(self):
    cls = self.__class__
    args = []
    for attr in self._attributes:
      if hasattr(self, attr):
        value = getattr(self, attr)
        args.append('{}={!r}'.format(attr, value))
    name = cls.__name__
    return '{}({})'.format(name, ', '.join(args))
    
  
class GET(Route):
  allowed_methods = frozenset(['GET'])

class POST(Route):
  allowed_methods = frozenset(['POST'])

class PUT(Route):
  allowed_methods = frozenset(['PUT'])

class PATCH(Route):
  allowed_methods = frozenset(['PATCH'])

class HEAD(Route):
  allowed_methods = frozenset(['HEAD'])

class DELETE(Route):
  allowed_methods = frozenset(['DELETE'])

class OPTIONS(Route):
  allowed_methods = frozenset(['OPTIONS'])

class TRACE(Route):
  allowed_methods = frozenset(['TRACE'])
