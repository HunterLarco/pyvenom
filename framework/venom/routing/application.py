# system imports
from collections import defaultdict

# package imports
import routes
from wsgi_entry import WSGIEntryPoint
import Protocols
from handlers import RequestHandler


__all__ = ['Application', 'VersionDispatch']


def generate_meta_handler(app):
  class MetaRouteHandler(RequestHandler):
    def serve(self):
      raw_path = self.path[len(app._meta_prefix):]
      if raw_path.startswith('/'): raw_path = raw_path[1:]
      path = '{}/{}'.format(app._api_prefix, raw_path)
      meta = { 'meta': True, 'routes': [] }
      for route in app.routes:
        if route.matches_path(path):
          meta['routes'].append({
            'url': dict(route._url),
            'query': dict(route._query),
            'body': dict(route._body),
            'methods': list(route.allowed_methods)
          })
      return meta
  return MetaRouteHandler


def generate_routes_handler(app):
  class GetRoutesHandler(RequestHandler):
    def serve(self):
      routes = defaultdict(set)
      for route in app.routes:
        if not route.path.startswith('/api/'): continue
        routes[route.path] = routes[route.path].union(route.allowed_methods)
      for route, methods in routes.items():
        routes[route] = list(methods)
      return {
        'routes': routes
      }
  return GetRoutesHandler


class _RoutesShortHand(WSGIEntryPoint):
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


class Application(_RoutesShortHand):
  allowed_methods = routes.Route.allowed_methods
  allowed_prefixes = frozenset(('api', 'meta', 'routes'))
  internal_protocol = Protocols.JSONProtocol
  
  def __init__(self, routes=None, version=1, protocol=Protocols.JSONProtocol):
    super(Application, self).__init__(protocol=protocol)
    self.routes = routes if routes else []
    self.version = version
    
    self._api_prefix = '/{}/v{}'.format('api', version)
    self._meta_prefix = '/{}/v{}'.format('meta', version)
    self._routes_prefix = '/{}/v{}'.format('routes', version)
    
    self._add_routes_route()
  
  def dispatch(self, request, response, error):
    route = self.find_route(request.path, request.method)
    if route == None:
      error(404)
      return
    route.handle(request, response, error)
  
  def find_route(self, path, method):
    for route in self.routes:
      if route.matches(path, method):
        return route
    return None
  
  def _add_route(self, path, handler, protocol, route_cls):
    if path.startswith('/'): path = path[1:]
    self._add_meta_route(path)
    return self._add_api_route(path, handler, protocol, route_cls)
  
  def _add_api_route(self, path, handler, protocol, route_cls):
    path = '{}/{}'.format(self._api_prefix, path)
    return super(Application, self)._add_route(path, handler, protocol, route_cls)
  
  def _add_meta_route(self, path):
    path = '{}/{}'.format(self._meta_prefix, path)
    return super(Application, self)._add_route(path, generate_meta_handler(self), self.internal_protocol, routes.Route)
  
  def _add_routes_route(self):
    return super(Application, self)._add_route(self._routes_prefix, generate_routes_handler(self), self.internal_protocol, routes.Route)
  
  def matches_version(self, path):
    for prefix in self.allowed_prefixes:
      prefix = '/{}/v{}/'.format(prefix, self.version)
      if path.startswith(prefix) or path == prefix[:-1]:
        return True
    return False


class VersionDispatch(WSGIEntryPoint):
  def __init__(self, *applications):
    super(VersionDispatch, self).__init__()
    self.applications = applications
  
  def dispatch(self, request, response, error):
    path = request.path
    for application in self.applications:
      if application.matches_version(path):
        return application
    error(404)
  