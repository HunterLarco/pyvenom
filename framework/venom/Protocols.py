import json


class Protocol(object):
  def __init__(self, headers=None):
    self.headers = headers if headers else {}
  
  def write(self, webapp2_response, error):
    webapp2_response.headers = self.headers
    webapp2_response.clear()


class JSONProtocol(Protocol):
  def __init__(self, data, headers=None):
    super(JSONProtocol, self).__init__(headers)
    self.headers['Content-Type'] = 'application/json'
    self.data = data
  
  def write(self, webapp2_response, error):
    super(JSONProtocol, self).write(webapp2_response, error)
    webapp2_response.write(json.dumps(self.data, indent=2))


class TextProtocol(Protocol):
  def __init__(self, data, headers=None):
    super(TextProtocol, self).__init__(headers)
    self.data = data
  
  def write(self, webapp2_response, error):
    super(TextProtocol, self).write(webapp2_response, error)
    webapp2_response.write(str(self.data))
    
