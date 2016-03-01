__all__ = []


from google.appengine.ext.webapp import template
import webapp2
import os
import mimetypes
import json


class ResourceHandler(webapp2.RequestHandler):
  def get(self, folder, path):
    path = os.path.join(os.path.dirname(__file__), 'templates/{}/{}'.format(folder, path))
    file = open(path, 'r').read()
    mime = mimetypes.guess_type(path)
    self.response.headers['Content-Type'] = mime[0]
    self.response.out.write(file)


class ScriptsHandler(webapp2.RequestHandler):
  def get(self):
    template_values = { 'scripts': sorted(scripts.keys()) }
    path = os.path.join(os.path.dirname(__file__), 'templates/scripts.html')
    self.response.out.write(template.render(path, template_values))


class MainHandler(webapp2.RequestHandler):
  def get(self):
    if not self.request.path.endswith('/'):
      self.redirect(self.request.path + '/')
      return


from cStringIO import StringIO
import sys

class Capturing(list):
  def __enter__(self):
    self._stdout = sys.stdout
    sys.stdout = self._stringio = StringIO()
    return self
  
  def __exit__(self, *args):
    self.extend(self._stringio.getvalue().splitlines())
    self._stringio.truncate(0)
    sys.stdout = self._stdout


class ScriptExecutionHandler(webapp2.RequestHandler):
  def post(self, script_name):
    if not script_name in scripts:
      self.error(500)
    script = scripts[script_name]
    with Capturing() as printed:
      try:
        returned = script()
      except Exception as err:
        returned = 'INTERNAL ERROR - {}'.format(err)
    try:
      self.response.out.write(json.dumps({
        'printed': printed,
        'returned': returned
      }))
    except TypeError:
      self.response.out.write(json.dumps({
        'printed': printed,
        'returned': str(returned)
      }))


ui = webapp2.WSGIApplication([
  ('.*/(resources|images)/(.*)', ResourceHandler),
  ('.*/scripts/?', ScriptsHandler),
  ('.*/scripts/execute/([^/]+)/?', ScriptExecutionHandler),
  ('.*', MainHandler)
], debug=True)








scripts = {}

def script(funct):
  scripts[funct.__name__] = funct
  return funct


import importutil
importutil.import_all()
