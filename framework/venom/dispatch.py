__all__ = ['Dispatcher', 'VersionDispatcher']


from wsgi_entry import WSGIEntryPoint


# can dispatch to other dispatchers or applications
class Dispatcher(WSGIEntryPoint):
  def __init__(self):
    super(Dispatcher, self).__init__()
    self.request = None
    self.response = None
    self.error = None
  
  def _on_entry(self, request, response, error):
    self.request = request
    self.response = response
    self.error = error
    new_wsgi = self.dispatch()
    if new_wsgi and hasattr(new_wsgi, '_on_entry'):
      new_wsgi._on_entry(request, response, error)
    else:
      error('404 Not Found')
    self.request = None
    self.response = None
    self.error = None
  
  def dispatch(self):
    raise NotImplemented()


class VersionDispatcher(Dispatcher):
  def __init__(self, *applications):
    super(VersionDispatcher, self).__init__()
    self.applications = applications
  
  def dispatch(self):
    for app in self.applications:
      if app.matches_prefix(self.request.path):
        return app
    return None