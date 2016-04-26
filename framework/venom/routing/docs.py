# system imports
import os

# package imports
from wsgi_entry import WSGIEntryPoint

# app engine imports
from google.appengine.ext.webapp import template


__all__ = 'Documentation'


class Documentation(WSGIEntryPoint):
  def __init__(self, application):
    super(Documentation, self).__init__()
    self.application = application
  
  def dispatch(self, request, response, error):
    template_values = {
      'version': self.application.version
    }
    path = os.path.join(os.path.dirname(__file__), 'docs/index.html')
    response.write(template.render(path, template_values))
