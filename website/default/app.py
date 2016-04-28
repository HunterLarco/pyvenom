from google.appengine.ext.webapp import template
import webapp2
import os


class DefaultHandler(webapp2.RequestHandler):
  def get(self):
    template_values = {}
    path = os.path.join(os.path.dirname(__file__), 'templates/landing.html')
    self.response.out.write(template.render(path, template_values))


app = webapp2.WSGIApplication([
  ('.*', DefaultHandler)
])