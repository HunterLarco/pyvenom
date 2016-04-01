__all__ = ['RequestHandler']


class RequestHandler(object):
  def __init__(self, route, webapp2_request, path):
    self.path = path
    self.method = webapp2_request.method.lower()
    self.route = route
    self.url = route._url.dispatch(route.get_url_variables(self.path))
    self.query = route._query.dispatch(webapp2_request.GET)
    
    try:
      body = json.loads(webapp2_request.body)
    except:
      body = webapp2_request.POST
    self.body = route._body.dispatch(body)
  
  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise NotImplementedError()