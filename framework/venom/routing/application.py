# system imports
from collections import defaultdict
import inspect

# package imports
import routes
from wsgi_entry import WSGIEntryPoint
import Protocols
from handlers import RequestHandler
from ..__ui__ import ui
from ..model import Model
import Parameters
from ..model import Properties
import docs


__all__ = ['Application', 'VersionDispatch']


def generate_meta_handler(app):
  class MetaRouteHandler(RequestHandler):
    def _removenull(self, obj):
      for key, value in obj.items():
        if value == None:
          del obj[key]
        if isinstance(value, dict):
          self._removenull(value)
      return obj
    
    def serve(self):
      raw_path = self.path[len(app._meta_prefix):]
      if raw_path.startswith('/'): raw_path = raw_path[1:]
      path = '{}/{}'.format(app._api_prefix, raw_path)
      meta = { 'meta': True, 'routes': [] }
      method = self.query.get('method')
      for route in app.routes:
        if method and not route.matches_method(method):
          continue
        if route.matches_path(path):
          
          docstring = ''
          if len(route.allowed_methods) != 1:
            docstring = route.handler.serve.__doc__
          else:
            route_method = list(route.allowed_methods)[0].lower()
            docstring = getattr(route.handler, route_method).__doc__
          if docstring:
            docstring = docstring.strip()
            docstring = '\n'.join([
              line.strip()
              for line in docstring.split('\n')
            ])
          
          meta['routes'].append({
            'headers': self._removenull(dict(route._headers)['template']),
            'url': self._removenull(dict(route._url)['template']),
            'query': self._removenull(dict(route._query)['template']),
            'body': self._removenull(dict(route._body)),
            'methods': list(route.allowed_methods),
            'ui.guid': ui.get_guid(route),
            'ui.handler_name': route.handler.__name__,
            'ui.handler_file': inspect.getsourcefile(route.handler),
            'ui.handler_body': ''.join(inspect.getsourcelines(route.handler)[0]),
            'path': route.path,
            'docstring': docstring
          })
      return meta
  return MetaRouteHandler


def generate_routes_handler(app):
  class GetRoutesHandler(RequestHandler):
    def serve(self):
      returned_routes = []
      
      for route in app.routes:
        if not route.path.startswith('/api/'): continue
        returned_routes.append({
          'path': route.path,
          'methods': list(route.allowed_methods),
          'ui.guid': ui.get_guid(route)
        })
      
      return {
        'routes': returned_routes,
        'version': app.version
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
  
  def CRUD(self, base_path, model, protocol=None):
    if not inspect.isclass(model):
      raise ValueError('Expected type venom.Model got {}'.format(model))
    if not issubclass(model, Model):
      raise ValueError('Expected type venom.Model got {}'.format(type(model)))
    
    if base_path.endswith('/'):
      base_path = base_path[:-1]
    
    body_params = model._to_route_parameters()
    patch_params = model._to_route_parameters()
    for key, param in patch_params.items():
      param.required = False
    
    class BaseHandler(RequestHandler):
      def get(self):
        """
        Return all entities for this model
        """
        query_name = self.query.get('query')
        if not query_name or not query_name in model._queries:
          query_name = 'all'
        query = model._queries[query_name]
        query_kwargs = {
          key: value
          for key, value in self.query.items()
          if key != 'query'
        }
        return {
          'entities': query(**query_kwargs),
          'query': query_name,
          'type': model.kind
        }
      
      def post(self):
        """
        Save a new entity to the database with the given body data
        """
        return model(**self.body).save()
      
    self._add_route(base_path, BaseHandler, protocol, routes.GET).query({
      'query': Parameters.String(required=False)
    })
    self._add_route(base_path, BaseHandler, protocol, routes.POST).body(body_params)
      
    class SpecificHandler(RequestHandler):
      def get(self):
        """
        Given an entity key, return the entity found in the database
        """
        return self.url.get('entity')
      
      def put(self):
        """
        Given an entity key, replace it's data with the provided body data
        """
        entity = self.url.get('entity')
        entity.populate(**self.body)
        return entity.save()
      
      def patch(self):
        """
        Given an entity key, alter any provided fields from the body data
        """
        entity = self.url.get('entity')
        entity.populate(**{
          key: value
          for key, value in self.body.items()
          if value != None
        })
        return entity.save()
      
      def delete(self):
        """
        Given an entity key, remove that entity from the database
        """
        self.url.get('entity').delete()
    
    path = '{}/:entity'.format(base_path)
    url_params = { 'entity': Parameters.Model(model) }
    self._add_route(path, SpecificHandler, protocol, routes.GET).url(url_params)
    self._add_route(path, SpecificHandler, protocol, routes.PUT).url(url_params).body(body_params)
    self._add_route(path, SpecificHandler, protocol, routes.PATCH).url(url_params).body(patch_params)
    self._add_route(path, SpecificHandler, protocol, routes.DELETE).url(url_params)


class Application(_RoutesShortHand):
  allowed_methods = routes.Route.allowed_methods
  allowed_prefixes = frozenset(('api', 'meta', 'routes', 'docs'))
  internal_protocol = Protocols.JSONProtocol
  
  default_errors = {
    Parameters.ParameterCastingFailed    : 1000,
    Parameters.ParameterValidationFailed : 1001,
    Properties.PropertyValidationFailed  : 2000,
  }
  
  def __init__(self, routes=None, version=1, protocol=Protocols.JSONProtocol, errors=None):
    super(Application, self).__init__(protocol=protocol)
    self.routes = routes if routes else []
    self.errors = errors if errors else {}
    self.version = version
    
    self.errors = dict(self.errors.items() + self.default_errors.items())
    
    self._api_prefix = '/{}/v{}'.format('api', version)
    self._meta_prefix = '/{}/v{}'.format('meta', version)
    self._routes_prefix = '/{}/v{}'.format('routes', version)
    self._docs_prefix = '/{}/v{}'.format('docs', version)
    
    self._add_routes_route()
  
  def dispatch(self, request, response, error):
    if self._matches_prefix(request.path, self._docs_prefix):
      return docs.Documentation(self)
    route = self.find_route(request.path, request.method)
    if route == None:
      error(404)
      return
    route.handle(request, response, error, errors=self.errors)
  
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
  
  def _matches_prefix(self, path, prefix):
    if not prefix.endswith('/'):
      prefix = '{}/'.format(prefix)
    return path.startswith(prefix) or path == prefix[:-1]


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
  