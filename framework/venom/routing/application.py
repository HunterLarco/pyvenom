# package imports
import routes
from wsgi_entry import WSGIEntryPoint
import Protocols


__all__ = ['Application']


class _RoutesShortHand(object):
  def __init__(self, routes=None, protocol=Protocols.JSONProtocol):
    super(_RoutesShortHand, self).__init__()
    self.protocol = protocol
    self.routes = routes if routes else []
  
  def _add_route(self, path, handler, protocol, route_cls):
    if not protocol: protocol = self.protocol
    route = route_cls(path, handler, protocol=protocol)
    self.routes.append(route)
    return route
  
  def GET(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.GET)
  
  def POST(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.POST)
  
  def PUT(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.PUT)
  
  def PATCH(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.PATCH)
  
  def HEAD(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.HEAD)
  
  def DELETE(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.DELETE)
  
  def OPTIONS(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.OPTIONS)
  
  def TRACE(self, path, handler, protocol=None):
    return self._add_route(path, handler, protocol, routes.TRACE)


class Application(WSGIEntryPoint, _RoutesShortHand):
  allowed_methods = routes.Route.allowed_methods
  allowable_prefixes = frozenset(('api', 'meta', 'routes'))
  
  def __init__(self, routes=None, version=1):
    super(Application, self).__init__()
    self.routes = routes if routes else []
    self.version = version
    
    self._api_prefix = '/{}/v{}'.format('api', version)
    self._meta_prefix = '/{}/v{}'.format('api', version)
    self._routes_prefix = '/{}/v{}'.format('api', version)
  
  def dispatch(self, request, response, error):
    route = self.find_route(request.path, request.method)
    if route == None:
      error(400)
      return
    route.handle(request, response, error)
  
  def find_route(self, path, method):
    for route in self.routes:
      if route.matches(path, method):
        return route
    return None
  
  