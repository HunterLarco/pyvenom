__all__ = ['WSGIEntryPoint']


import webapp2


class WSGIEntryPoint(object):
  allowed_methods = frozenset((
    'GET', 'POST', 'PUT', 'PATCH',
    'HEAD', 'DELETE', 'OPTIONS', 'TRACE'
  ))
  
  def __init__(self):
    super(WSGIEntryPoint, self).__init__()
    self._form_request_handler()
    self.wsgi = webapp2.WSGIApplication([('.*', self._entrypoint)], debug=False)
    self.wsgi.allowed_methods = self.allowed_methods
  
  def dispatch(self, request, response, error):
    raise NotImplementedError()
  
  def _form_request_handler(self):
    wsgientry = self
    class MainHandler(webapp2.RequestHandler):
      def dispatch(self):
        new_wsgi = wsgientry.dispatch(self.request, self.response, self.error)
        if isinstance(new_wsgi, WSGIEntryPoint):
          return new_wsgi
    self._entrypoint = MainHandler
  
  def __call__(self, *args, **kwargs):
    return self.wsgi(*args, **kwargs)