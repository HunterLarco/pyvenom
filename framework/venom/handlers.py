__all__ = ['RequestHandler']


class HTTPMethodNotImplemented(Exception):
  pass


class RequestHandler(object):
  def __init__(self, route, request, response, error):
    self.route = route
    self.method = request.method.lower()

  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise HTTPMethodNotImplemented('HTTP Method {} not implemented when expected'.format(method.upper()))
