# system imports
import traceback
import json


__all__ = ['Protocol', 'TextProtocol', 'JSONProtocol']


class Protocol(object):
  def __init__(self, request, response, error):
    super(Protocol, self).__init__()
    self.request = request
    self.response = response
    self.error = error
  
  def _read(self, value):
    return self.read(value)
  
  def _write(self, value):
    written = self.write(value)
    self.response.write(written)
    return written
  
  def _apply_headers(self):
    for key, value in self.headers().items():
      self.response.headers[key] = value
  
  def headers(self):
    return {}
  
  def read(self, value):
    raise NotImplementedError('Protocol read method not implemented')
  
  def write(self, value):
    raise NotImplementedError('Protocol write method not implemented')
  
  def __enter__(self):
    return self
  
  def __exit__(self, exception_type, exception_value, exception_traceback):
    if exception_type:
      self._exit_error(exception_type, exception_value, exception_traceback)
    else:
      self._exit_success()
    return True
  
  def _exit_error(self, exception_type, exception_value, exception_traceback):
    self._apply_headers()
    self.error(500)
    traceback.print_exc()
    try:
      self._write({
        'message': 'An unknown error occured'
      })
    except Exception:
      traceback.print_exc()
  
  def _exit_success(self):
    self._apply_headers()
    

class TextProtocol(Protocol):
  def headers(self):
    return { 'content-type': 'text/plain' }
  
  def write(self, value):
    if not value: value = ''
    return str(value)
  
  def read(self, value):
    if not value: return ''
    return str(value)


class JSONProtocol(Protocol):
  def headers(self):
    return { 'content-type': 'application/json' }
  
  def write(self, value):
    if not value: value = {}
    return json.dumps(value, indent=2, sort_keys=True)
  
  def read(self, value):
    if not value: return {}
    return json.loads(value)