__all__ = ['Servable', 'RequestHandler']


class Servable(object):
  def __init__(self, request, response, error, route):
    super(Servable, self).__init__()
    self.request = request
    self.response = response
    self.error = error
    self.route = route
  
  def serve(self):
    raise NotImplementedError()


class RequestHandler(Servable):
  def __init__(self, request, response, error, route):
    self.path = request.path
    self.route = route
    self.method = request.method.lower()
    # self.url = ParameterDict(url_params)
    # self.query = ParameterDict(query_params)
    # self.body = ParameterDict(body_params)
  
  def serve(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise Exception('HTTP Method {} not implemented when expected'.format(method.upper()))

