__all__ = ['scaffold']
import scaffold


from google.appengine.ext.webapp import template
import webapp2
import os
import mimetypes
import json
import email.Utils
import time


mimetypes.add_type("image/svg+xml", ".svg")


class ResourceHandler(webapp2.RequestHandler):
  def get(self, folder, path):
    here = os.path.dirname(__file__)
    fn = os.path.join(here, 'templates/{}/{}'.format(folder, path))
    ctype, encoding = mimetypes.guess_type(fn)
    assert ctype and '/' in ctype, repr(ctype)
    expiry = 3600
    expiration = email.Utils.formatdate(time.time() + expiry, usegmt=True)
    fp = open(fn, 'rb')
    try:
      self.response.out.write(fp.read())
    finally:
      fp.close()
    self.response.headers['Content-type'] = ctype
    self.response.headers['Cache-Control'] = 'public, max-age=expiry'
    self.response.headers['Expires'] = expiration


class ScriptsHandler(webapp2.RequestHandler):
  def get(self):
    templated = [[key, value[1]] for key, value in scripts.items()]
    template_values = { 'scripts': sorted(templated) }
    path = os.path.join(os.path.dirname(__file__), 'templates/scripts.html')
    self.response.out.write(template.render(path, template_values))


class ScaffoldHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates/scaffold.html')
    self.response.out.write(template.render(path, template_values))


class MainHandler(webapp2.RequestHandler):
  def get(self):
    if not self.request.path.endswith('/'):
      self.redirect(self.request.path + '/')
      return
    
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates/main.html')
    self.response.out.write(template.render(path, template_values))


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
      return self.error(500)
    script = scripts[script_name][0]
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
  ('.*/scripts', ScriptsHandler),
  ('.*/scaffold', ScaffoldHandler),
  ('.*/scripts/execute/([^/]+)/?', ScriptExecutionHandler),
  ('.*', MainHandler)
], debug=True)








scripts = {}

def script(funct):
  doc = funct.__doc__ if funct.__doc__ else 'No Documentation'
  scripts[funct.__name__] = (funct, doc)
  return funct


import importutil
importutil.import_all()
