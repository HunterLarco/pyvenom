import webapp2

import routes
import Protocols


__all__ = ['Application']


class Application(object):
  def __init__(self, version=1, routes=None, debug=False):
    self.version = version
    self.api_prefix = '/api/v{}/'.format(version)
    self.meta_prefix = '/meta/v{}/'.format(version)
    self.docs_prefix = '/docs/v{}/'.format(version)
    self.routes = routes if routes else []
    self.debug = debug
    self._form_request_handler()
    self.wsgi = webapp2.WSGIApplication([('.*', self._entrypoint)], debug=False)
  
  def GET(self, *args, **kwargs):
    route = routes.GET(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def POST(self, *args, **kwargs):
    route = routes.POST(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def PUT(self, *args, **kwargs):
    route = routes.PUT(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def PATCH(self, *args, **kwargs):
    route = routes.PATCH(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def DELETE(self, *args, **kwargs):
    route = routes.DELETE(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def OPTIONS(self, *args, **kwargs):
    route = routes.OPTIONS(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def HEAD(self, *args, **kwargs):
    route = routes.HEAD(*args, **kwargs)
    self.routes.append(route)
    return route
  
  def _form_request_handler(self):
    server = self
    class MainHandler(webapp2.RequestHandler):
      def dispatch(self):
        server.route(self.request, self.response, self.error)
    self._entrypoint = MainHandler
  
  def __call__(self, *args, **kwargs):
    return self.wsgi(*args, **kwargs)
  
  def write_protocol(self, protocol, request, response, error):
    if not protocol: protocol = Protocols.Protocol()
    protocol.write(response, error)
  
  def _clean_path(self, path):
    if path.startswith(self.api_prefix):
      path = path[len(self.api_prefix):]
    elif path.startswith(self.meta_prefix):
      path = path[len(self.meta_prefix):]
    elif path.startswith(self.docs_prefix):
      path = path[len(self.docs_prefix):]
    return path
  
  def _get_route_from_path(self, path, method):
    for route in self.routes:
      if route.matches(path, method):
        return route
  
  def route(self, request, response, error):
    path = self._clean_path(request.path)
    route = self._get_route_from_path(path, request.method)
    
    if not route:
      error(404)
      response.write('404 Not Found')
      return
    
    if request.path.startswith(self.api_prefix):
      protocol = route.dispatch(request, path)
    elif request.path.startswith(self.meta_prefix):
      protocol = Protocols.JSONProtocol({
        'parameters': {
          'body': route._body.metadict()['children'],
          'url': route._url.metadict()['children'],
          'query': route._query.metadict()['children']
        },
        'path': route.path
      })
    elif request.path.startswith(self.docs_prefix):
      protocol = Protocols.TextProtocol('In Progress')
    else:
      protocol = Protocols.TextProtocol('Unknown Prefix')
    
    self.write_protocol(protocol, request, response, error)
      
