__all__ = ['Protocol']


class ProtocolReadFailed(Exception):
  pass

class ProtocolWriteFailed(Exception):
  pass


class Protocol(object):
  def __init__(self, request, response, error):
    self.request = request
    self.response = response
    self.error = error
    self._writing_error = False
  
  def _read(self, value):
    try:
      return self.read(value)
    except Exception:
      raise ProtocolReadFailed('Protocol read failed')
  
  def read(self, value):
    raise NotImplementedError('Protocol read method not implemented')
  
  def _write(self, value):
    try:
      return self.write(value)
    except Exception:
      raise ProtocolWriteFailed('Protocol write failed')
  
  def write(self, value):
    raise NotImplementedError('Protocol write method not implemented')
  
  def __enter__(self):
    return self
  
  def __exit__(self, exception_type, exception_value, traceback):
    if not exception_type: return
    self.error(500)
    if self._writing_error: return False
    self._writing_error = True
    self.write({
      'success': False,
      'message': exception_value.message
    })
    return True# suppresses exception


class JSONProtocol(Protocol):
  def read(self, value):
    if not value: value = '{}'
    from json import loads
    return loads(value)
  
  def write(self, value):
    from json import dumps
    self.response.write(dumps(value, indent=2))
