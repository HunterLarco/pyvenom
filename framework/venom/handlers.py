__all__ = ['RequestHandler']


class HTTPMethodNotImplemented(Exception):
  pass


class RequestHandler(object):
  def __init__(self, route, request, url_params, query_params, body_params):
    self.path = request.path
    self.route = route
    self.method = request.method.lower()
    self.url = ParameterDict(url_params)
    self.query = ParameterDict(query_params)
    self.body = ParameterDict(body_params)

  def dispatch(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise HTTPMethodNotImplemented('HTTP Method {} not implemented when expected'.format(method.upper()))


class ParameterList(list):
  def __init__(self, *args, **kwargs):
    super(ParameterList, self).__init__(*args, **kwargs)
    self._sanitize()
  
  def _sanitize(self):
    for i, item in enumerate(self):
      if isinstance(item, dict):
        self[i] = ParameterDict(item)
      elif isinstance(item, list):
        self[i] = ParameterList(item)
  
  def get(self, *paths):
    if not paths: return None
    if len(paths) == 1: return self._get(paths[0])
    return [self._get(path) for path in paths]
  
  def _get(self, path):
    if not path: return self
    response = []
    for item in self:
      response.append(item.get(path))
    return response


class ParameterDict(dict):
  def __init__(self, *args, **kwargs):
    super(ParameterDict, self).__init__(*args, **kwargs)
    self._sanitize()
  
  def _sanitize(self):
    for key, value in self.items():
      if isinstance(value, dict):
        self[key] = ParameterDict(value)
      elif isinstance(value, list):
        self[key] = ParameterList(value)
  
  def get(self, *paths):
    if not paths: return None
    if len(paths) == 1: return self._get(paths[0])
    return [self._get(path) for path in paths]
  
  def _get(self, path):
    if not path: return self
    section = path.split('.')[0]
    rest = '.'.join(path.split('.')[1:])
    
    if not section in self: return None
    
    if rest:
      return self[section].get(rest)
    return self[section]
