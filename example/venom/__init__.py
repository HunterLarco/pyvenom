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


class PageHandler(webapp2.RequestHandler):
  def get(self, page):
    pass


class MainHandler(webapp2.RequestHandler):
  def get(self):
    if not self.request.path.endswith('/'):
      self.redirect(self.request.path + '/')
      return
    
    template_values = {
      'scripts': sorted(scripts.keys())
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/scripts.html')
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
  ('.*/(scripts|endpoints|models|scaffold)', PageHandler),
  ('.*/scripts/execute/([^/]+)/?', ScriptExecutionHandler),
  ('.*', MainHandler)
], debug=True)








scripts = {}

def script(funct):
  scripts[funct.__name__] = funct
  return funct


def importEverything():
  path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
  modules = find_files(path, pattern='*.py')
  for module in modules:
    name = file_to_module(module)
    __import__(name, globals(), locals(), [], -1)

def find_files(directory, pattern='*'):
  import fnmatch
  
  if not os.path.exists(directory):
    raise ValueError("Directory not found {}".format(directory))

  matches = []
  for root, dirnames, filenames in os.walk(directory):
    
    dirname = os.path.dirname(__file__)
    common_prefix = os.path.commonprefix([dirname, root])
    if common_prefix == dirname: continue
    
    for filename in filenames:
      full_path = os.path.join(root, filename)
      if fnmatch.filter([full_path], pattern):
        matches.append(os.path.join(root, filename))
  
  return matches

def file_to_module(full_path_to_module):
  common_prefix = os.path.commonprefix([__file__, full_path_to_module])
  relative = os.path.relpath(full_path_to_module, common_prefix)[:-3]
  relative = relative.replace('./', '/')
  relative = relative.replace('../', './')
  relative = relative.replace('/', '.')
  return relative
      

importEverything()
