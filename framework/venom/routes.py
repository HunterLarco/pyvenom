__all__ = ['Route', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'TRACE']


# system imports
import json

# application imports
# import Parameters


class Route(object):
  DEFAULT_METHOD = None
  
  def __init__(self, path, handler):
    self.method = self.DEFAULT_METHOD
    self.path = path
    # self._url = Parameters.Dict({})
    # self._body = Parameters.Dict({})
    # self._query = Parameters.Dict({})
    self.handler = handler
  
  def sanitize_path(self, path):
    if path.endswith('/'): path = path[:-1]
    if path.startswith('/'): path = path[1:]
    return path
  
  def matches(self, request):
    return self.get_url_variables(request) is not None
  
  def get_url_variables(self, request):
    path = request.path
    method = request.method
    
    if self.method and self.method.lower() != method.lower(): return None
    
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
    response.write('FOUND {}'.format(self.path))
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



