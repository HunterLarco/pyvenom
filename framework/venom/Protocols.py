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
    self._success = True
  
  def _read(self, value):
    try:
      return self.read(value)
    except Exception:
      raise ProtocolReadFailed('Protocol read failed')
  
  def read(self, value):
    raise NotImplementedError('Protocol read method not implemented')
  
  def _catch_write(self, value):
    try:
      return self._pre_write(value)
    except Exception:
      raise ProtocolWriteFailed('Protocol write failed')
  
  def _pre_write(self, value):
    value['success'] = self._success
    self.write(value)
  
  def write(self, value):
    raise NotImplementedError('Protocol write method not implemented')
  
  def __enter__(self):
    return self
  
  def __exit__(self, exception_type, exception_value, traceback):
    if not exception_type: return
    self.error(500)
    if not self._success: return False
    self._success = False
    self._pre_write({
      'message': exception_value.message
    })
    return True# suppresses exception


class JSONProtocol(Protocol):
  def read(self, value):
    if not value: value = '{}'
    from json import loads
    return loads(value)
  
  def write(self, value):
    if not value: value = {}
    from json import dumps
    self.response.write(dumps(value, indent=2))
