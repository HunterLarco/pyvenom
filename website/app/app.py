import webapp2


class DefaultHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write('test app')


app = webapp2.WSGIApplication([
  ('.*', DefaultHandler)
])