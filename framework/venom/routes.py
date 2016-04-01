__all__ = ['Route', 'GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS', 'HEAD']


import json

import Parameters


class Route(object):
  DEFAULT_METHOD = None
  
  def __init__(self, path, handler):
    self.method = self.DEFAULT_METHOD
    self.path = path
    self._url = Parameters.Dict({})
    self._body = Parameters.Dict({})
    self._query = Parameters.Dict({})
    self.handler = handler
  
  def matches(self, path):
    if path.endswith('/'): path = path[:-1]
    
    templatefolders = self.path.split('/')
    folders = path.split('/')
    
    if len(templatefolders) != len(folders): return False
    
    for templatefolder, folder in zip(templatefolders, folders):
      if not templatefolder.startswith(':') and  templatefolder != folder:
        return False
    
    return True
  
  def get_url_variables(self, path):
    variables = {}
    
    if path.endswith('/'): path = path[:-1]
    
    templatefolders = self.path.split('/')
    folders = path.split('/')
    
    if len(templatefolders) != len(folders): return False
    
    for templatefolder, folder in zip(templatefolders, folders):
      if templatefolder.startswith(':'):
        variables[templatefolder[1:]] = folder
      elif templatefolder != folder:
        return None
    
    return variables
  
  def dispatch(self, webapp2_request):
    return self.handler(self, webapp2_request).dispatch()
    
  def url(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._url = params
    return self
  
  def body(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._body = params
    return self
  
  def query(self, params):
    if isinstance(params, dict):
      params = Parameters.Dict(params)
    self._query = params
    return self
  

class GET(Route):
  DEFAULT_METHOD = 'GET'

class POST(Route):
  DEFAULT_METHOD = 'POST'

class PUT(Route):
  DEFAULT_METHOD = 'PUT'

class PATCH(Route):
  DEFAULT_METHOD = 'PATCH'

class DELETE(Route):
  DEFAULT_METHOD = 'DELETE'

class OPTIONS(Route):
  DEFAULT_METHOD = 'OPTIONS'

class HEAD(Route):
  DEFAULT_METHOD = 'HEAD'



