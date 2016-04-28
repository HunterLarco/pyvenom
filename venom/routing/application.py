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



def _removenull(obj):
  for key, value in obj.items():
    if value == None:
      del obj[key]
    if isinstance(value, dict):
      _removenull(value)
  return obj


def route_to_meta(route):
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
  
  return {
    'headers': _removenull(dict(route._headers)['template']),
    'url': _removenull(dict(route._url)['template']),
    'query': _removenull(dict(route._query)['template']),
    'body': _removenull(dict(route._body)),
    'methods': list(route.allowed_methods),
    'ui.guid': ui.get_guid(route),
    'ui.handler_name': route.handler.__name__,
    'ui.handler_file': inspect.getsourcefile(route.handler),
    'ui.handler_body': ''.join(inspect.getsourcelines(route.handler)[0]),
    'path': route.path,
    'docstring': docstring
  }


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
          meta['routes'].append(route_to_meta(route))
      return meta
  return MetaRouteHandler


def generate_routes_handler(app):
  class GetRoutesHandler(RequestHandler):
    def serve(self):
      returned_routes = []
      
      guid = self.query.get('uiguid')
      
      for route in app.routes:
        if not route.path.startswith('/api/'): continue
        if guid and ui.get_guid(route) == guid:
          return { 'route': route_to_meta(route) }
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
  
  def CRUD(self, base_path, model, protocol=None, domain=None):
    if not inspect.isclass(model):
      raise ValueError('Expected type venom.Model got {}'.format(model))
    if not issubclass(model, Model):
      raise ValueError('Expected type venom.Model got {}'.format(type(model)))
    
    if base_path.endswith('/'):
      base_path = base_path[:-1]
    
    url_params = {}
    if domain:
      url_params = { domain: getattr(model, domain).to_route_parameter() }
    
    body_params = model._to_route_parameters()
    if domain and domain in body_params:
      del body_params[domain]
    
    patch_params = model._to_route_parameters()
    for key, param in patch_params.items():
      param.required = False
    
    class BaseHandler(RequestHandler):
      def get(self):
        """
        Return all entities for this model
        """
        if domain:
          results = model._owners[domain](self.url.get(domain))
        else:
          results = model.all()
        return {
          'entities': results,
          'type': model.kind
        }
      
      def post(self):
        """
        Save a new entity to the database with the given body data
        """
        entity = model(**self.body)
        if domain:
          setattr(entity, domain, self.url.get(domain))
        return entity.save()
      
    self._add_route(base_path, BaseHandler, protocol, routes.GET).url(url_params)
    self._add_route(base_path, BaseHandler, protocol, routes.POST).body(body_params).url(url_params)
      
    class SpecificHandler(RequestHandler):
      def _check_ownership(self):
        entity = self.url.get('entity')
        if domain:
          owner = self.url.get(domain)
          if getattr(entity, domain).key != owner.key:
            raise Exception('Invalid ownership')
      
      def get(self):
        """
        Given an entity key, return the entity found in the database
        """
        self._check_ownership()
        return self.url.get('entity')
      
      def put(self):
        """
        Given an entity key, replace it's data with the provided body data
        """
        self._check_ownership()
        entity = self.url.get('entity')
        entity.populate(**self.body)
        return entity.save()
      
      def patch(self):
        """
        Given an entity key, alter any provided fields from the body data
        """
        self._check_ownership()
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
        self._check_ownership()
        self.url.get('entity').delete()
    
    path = '{}/:entity'.format(base_path)
    url_params = dict({ 'entity': Parameters.Model(model) }.items() + url_params.items())
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
  
  def __init__(self, routes=None, version=1, packages=None, protocol=Protocols.JSONProtocol, errors=None):
    super(Application, self).__init__(protocol=protocol)
    self.routes = routes if routes else []
    self.errors = errors if errors else {}
    self.version = version
    self.packages = []
    
    self.errors = dict(self.errors.items() + self.default_errors.items())
    
    self._api_prefix = '/{}/v{}'.format('api', version)
    self._meta_prefix = '/{}/v{}'.format('meta', version)
    self._routes_prefix = '/{}/v{}'.format('routes', version)
    self._docs_prefix = '/{}/v{}'.format('docs', version)
    
    self._add_routes_route()
    
    if packages and not isinstance(packages, list):
      packages = [packages]
    self._load_packages(packages)
  
  def _load_packages(self, packages):
    if not packages: return
    for package in packages:
      self.load_package(package)
    
  def load_package(self, package):
    if not hasattr(package, 'package'):
      raise AttributeError('Venom Package must have package(app) method')
    getattr(package, 'package')(self)
    self.packages.append(package)
  
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
  