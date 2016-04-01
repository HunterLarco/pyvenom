__all__ = ['RequestHandler']


class RequestHandler(object):
  def __init__(self, route, request, response, error):
    self.route = route
    self.method = request.method.lower()

  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise NotImplementedError()
