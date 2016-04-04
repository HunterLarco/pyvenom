__all__ = ['Application']


# system imports
from collections import defaultdict

# application imports
from wsgi_entry import WSGIEntryPoint
import routes
import Protocols
from handlers import RequestHandler


def generate_meta_handler(app):
  class MetaRouteHandler(RequestHandler):
    def dispatch(self):
      prefix = '/meta/v{}/'.format(app.version)
      path = '/api/v{}/{}'.format(app.version, self.path[len(prefix):])
      meta = { 'meta': True }
      for route in app.routes:
        if route.matches_path(path):
          meta[route.method] = {
            'url': route._url.to_meta_dict(),
            'query': route._query.to_meta_dict(),
            'body': route._body.to_meta_dict()
          }
      return meta
  return MetaRouteHandler


def generate_routes_handler(app):
  class GetRoutesHandler(RequestHandler):
    def dispatch(self):
      routes = defaultdict(set)
      for route in app.routes:
        if not route.path.startswith('/api/'): continue
        if not route.method:
          routes[route.path] = routes[route.path].union(app.allowable_methods)
        else:
          routes[route.path].add(route.method)
      for route, methods in routes.items():
        routes[route] = list(methods)
      return {
        'routes': routes
      }
  return GetRoutesHandler


class Application(WSGIEntryPoint):
  allowable_methods = frozenset(('GET', 'POST', 'PUT', 'PATCH', 'HEAD', 'DELETE', 'OPTIONS', 'TRACE'))
  allowable_prefixes = frozenset(('api', 'meta', 'docs', 'routes'))
  
  def __init__(self, routes=None, version=1, debug=False, protocol=None):
    super(Application, self).__init__()
    self.routes = routes if routes else []
    self.version = version
    self.debug = debug
    self.protocol = protocol
    self._add_routes_route()
  
  def matches_prefix(self, path):
    for prefix in self.allowable_prefixes:
      prefixed_path = '/{}/v{}'.format(prefix, self.version)
      if path.startswith('{}/'.format(prefixed_path)) or path == prefixed_path:
        return True
    return False
  
  def _on_entry(self, request, response, error):
    for route in self.routes:
      if route.matches(request.path, request.method):
        route.execute(request, response, error)
        return
    error(404)
  
  def _add_routes_route(self):
    path = '/routes/v{}'.format(self.version)
    route = routes.Route(path, generate_routes_handler(self), Protocols.JSONProtocol)
    self.routes.append(route)
    return route
  
  def _add_meta_route(self, path, handler, protocol):
    path = '/meta/v{}/{}'.format(self.version, path)
    route = routes.Route(path, generate_meta_handler(self), Protocols.JSONProtocol)
    self.routes.append(route)
    return route
  
  def _add_route(self, path, handler, protocol, route_cls):
    if not protocol: protocol = self.protocol
    if path.startswith('/'): path = path[1:]
    
    self._add_meta_route(path, handler, protocol)
    
    path = '/api/v{}/{}'.format(self.version, path)
    route = route_cls(path, handler, protocol)
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
  