__all__ = ['Route', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE']


# system imports
import json

# application imports
import Parameters


class Route(object):
  DEFAULT_METHOD = None
  
  def __init__(self, path, handler, protocol):
    self.method = self.DEFAULT_METHOD
    self.path = path
    self._url = Parameters.Dict({})
    self._body = Parameters.Dict({})
    self._query = Parameters.Dict({})
    self.handler = handler
    self.protocol = protocol
  
  def sanitize_path(self, path):
    if path.endswith('/'): path = path[:-1]
    if path.startswith('/'): path = path[1:]
    return path
  
  def matches(self, path, method):
    return self.matches_path(path) and self.matches_method(method)
  
  def matches_method(self, method):
    return not self.method or self.method.lower() == method.lower()
  
  def matches_path(self, path):
    return self.get_url_variables(path) is not None
  
  def get_url_variables(self, path):
    variables = {}
    
    live_path = self.sanitize_path(path)
    route_path = self.sanitize_path(self.path)
    
    live_sections = live_path.split('/')
    route_sections = route_path.split('/')
    
    if len(live_sections) != len(route_sections): return None
    
    for live_section, route_section in zip(live_sections, route_sections):
      if route_section.startswith(':'):
        variables[route_section[1:]] = live_section
      elif live_section != route_section:
        return None
    
    return variables
  
  def execute(self, request, response, error):
    with self.protocol(request, response, error) as proto:
      body_params = proto._read(request.body)
      query_params = request.GET
      url_params = self.get_url_variables(request.path)
      
      body_params = self._body.load(body_params)
      query_params = self._query.load(url_params)
      query_params = self._url.load(url_params)
      
      handler = self.handler(self, request, response, error)
      returned = handler.dispatch()
      proto._catch_write(returned)
    # return self.handler(self, request, response, error).dispatch()
    
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
  

class GET(Route):
  DEFAULT_METHOD = 'GET'

class POST(Route):
  DEFAULT_METHOD = 'POST'

class PUT(Route):
  DEFAULT_METHOD = 'PUT'

class PATCH(Route):
  DEFAULT_METHOD = 'PATCH'

class DELETE(Route):
  DEFAULT_METHOD = 'DELETE'

class OPTIONS(Route):
  DEFAULT_METHOD = 'OPTIONS'

class HEAD(Route):
  DEFAULT_METHOD = 'HEAD'

class TRACE(Route):
  DEFAULT_METHOD = 'TRACE'



