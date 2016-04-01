__all__ = ['Application']


# application imports
from wsgi_entry import WSGIEntryPoint
import routes



class Application(WSGIEntryPoint):
  allowable_prefixes = frozenset(('api', 'meta', 'docs'))
  
  def __init__(self, routes=None, version=1, debug=False):
    super(Application, self).__init__()
    self.routes = routes if routes else []
    self.version = version
    self.debug = debug
  
  def matches_prefix(self, path):
    for prefix in self.allowable_prefixes:
      if path.startswith('/{}/v{}/'.format(prefix, self.version)):
        return True
    return False
  
  def _on_entry(self, request, response, error):
    for route in self.routes:
      if route.matches(request):
        route.execute(request, response, error)
        return
    error(404)
  
  def _add_route(self, path, handler, protocol, route_cls):
    if path.startswith('/'): path = path[1:]
    path = '/api/v{}/'.format(self.version) + path
    route = route_cls(path, handler, protocol)
    self.routes.append(route)
    return route
  
  def GET(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.GET)
  
  def POST(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.POST)
  
  def PUT(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.PUT)
  
  def PATCH(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.PATCH)
  
  def HEAD(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.HEAD)
  
  def DELETE(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.DELETE)
  
  def OPTIONS(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.OPTIONS)
  
  def TRACE(self, path, handler, protocol):
    return self._add_route(path, handler, protocol, routes.TRACE)
  