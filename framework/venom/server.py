import webapp2

import routes
import Protocols


__all__ = ['Server']


class Server(object):
  def __init__(self, routes=None, debug=False):
    self.routes = routes if routes else []
    self.debug = debug
    self._form_request_handler()
    self.wsgi = webapp2.WSGIApplication([('.*', self._entrypoint)], debug=False)
    self.wsgi.allowed_methods = frozenset(('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD', 'META'))
  
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
  
  def route(self, request, response, error):
    for route in self.routes:
      if route.matches(request.path):
        if request.method.upper() == 'META':
          protocol = Protocols.JSONProtocol({
            'parameters': {
              'body': route._body.metadict()['children'],
              'url': route._url.metadict()['children'],
              'query': route._query.metadict()['children']
            },
            'path': route.path
          })
          self.write_protocol(protocol, request, response, error)
          return
        if route.method and route.method.upper() == request.method.upper():
          protocol = route.dispatch(request)
          self.write_protocol(protocol, request, response, error)
          return
    error(404)
    response.write('404 Not Found')
      
