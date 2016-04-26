__all__ = ['Servable', 'RequestHandler']


class Servable(object):
  _attributes = ['route', 'protocol']
  
  def __init__(self, request, response, error, route, protocol):
    super(Servable, self).__init__()
    self.request = request
    self.response = response
    self.error = error
    self.route = route
    self.protocol = protocol
  
  def serve(self):
    raise NotImplementedError()
  
  def __repr__(self):
    cls = self.__class__
    args = []
    for attr in self._attributes:
      if hasattr(self, attr):
        value = getattr(self, attr)
        args.append('{}={!r}'.format(attr, value))
    name = cls.__name__
    return '{}({})'.format(name, ', '.join(args))


class RequestHandler(Servable):
  _attributes = ['path', 'method']
  
  def __init__(self, request, response, error, route, protocol):
    self.path = request.path
    self.route = route
    self.method = request.method.lower()
    
    self.url = ParameterDict(self._get_url_parameters())
    self.query = ParameterDict(self._get_query_parameters(request))
    self.headers = HeaderDict(self._get_headers_parameters(request))
    self.body = ParameterDict(self._get_body_parameters(request, protocol))
    
    self.throw = error
  
  def _get_headers_parameters(self, request):
    return self.route._headers.load('request.Headers', request.headers)
  
  def _get_query_parameters(self, request):
    return self.route._query.load('request.Query', request.GET)
  
  def _get_url_parameters(self):
    path_params = self.route.path.get_parameters(self.path)
    return self.route._url.load('request.Path', path_params)
  
  def _get_body_parameters(self, request, protocol):
    body = protocol._read(request.body)
    return self.route._body.load('request.Body', body)
  
  def serve(self):
    method = self.method.lower()
    if hasattr(self, method):
      return getattr(self, method)()
    raise Exception('HTTP Method {} not implemented when expected'.format(method.upper()))


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


class HeaderDict(ParameterDict):
  def __init__(self, obj):
    obj = dict(obj)
    for key, value in obj.items():
      self[key] = value
  
  def __getitem__(self, key):
    return super(HeaderDict, self).__getitem__(key.lower())
  
  def __setitem__(self, key, value):
    return super(HeaderDict, self).__setitem__(key.lower(), value)
    
    
