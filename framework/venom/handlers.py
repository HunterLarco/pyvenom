__all__ = ['RequestHandler']


class HTTPMethodNotImplemented(Exception):
  pass


class RequestHandler(object):
  def __init__(self, route, request, url_params, query_params, body_params):
    self.path = request.path
    self.route = route
    self.method = request.method.lower()
    self.url = url_params
    self.query = query_params
    self.body = body_params

  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise HTTPMethodNotImplemented('HTTP Method {} not implemented when expected'.format(method.upper()))
