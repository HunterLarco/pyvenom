__all__ = ['RequestHandler']


class RequestHandler(object):
  def __init__(self, webapp2_request):
    self.method = webapp2_request.method.lower()
  
  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise NotImplemented()