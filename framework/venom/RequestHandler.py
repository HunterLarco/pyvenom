# system imports
import json

# app engine imports
import webapp2

# application imports
from ParameterDict import *


__all__ = ['RequestHandler']


class Request(object):
  def __init__(self, webapp2_request):
    self._request = webapp2_request
    
    self.body = self._load_body_dict()
    self.query = self._load_query_dict()
    
    # dispatch compliance
    self.route_kwargs = self._request.route_kwargs
    self.route_args   = self._request.route_args
    self.method       = self._request.method
    self.route        = self._request.route
  
  def _load_body_dict(self):
    data = self._request.POST
    headers = self._request.headers
    if 'Content-Type' in headers and headers['Content-Type'].lower().endswith('json'):
      try:
        return ParameterDict(json.loads(self._request.body))
      except ValueError:
        return ParameterDict(data)
    return ParameterDict(data)
  
  def _load_query_dict(self):
    return ParameterDict(self._request.GET)


class RequestHandler(webapp2.RequestHandler):
  def dispatch(self):
    self.request = Request(self.request)
    return super(RequestHandler, self).dispatch()
    
