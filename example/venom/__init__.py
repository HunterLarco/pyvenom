__all__ = []


from google.appengine.ext.webapp import template
import webapp2
import os
import mimetypes


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
    
    script_names = map(lambda x: x.__name__, scripts)
    
    template_values = {
      'scripts': script_names
    }
    path = os.path.join(os.path.dirname(__file__), 'templates/scripts.html')
    self.response.out.write(template.render(path, template_values))


ui = webapp2.WSGIApplication([
  ('.*/(resources|images)/(.*)', ResourceHandler),
  ('.*/(scripts|endpoints|models|scaffold)', PageHandler),
  ('.*', MainHandler)
], debug=True)








scripts = []

def script(funct):
  scripts.append(funct)
  return funct
  
  
import app