__all__ = ['Servable', 'RequestHandler']


class Servable(object):
  def __init__(self, request, response, error):
    super(Servable, self).__init__()
    self.request = request
    self.response = response
    self.error = error
  
  def serve(self):
    raise NotImplementedError()


class RequestHandler(Servable):
  pass

