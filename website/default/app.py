import webapp2


class DefaultHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write('test default')


app = webapp2.WSGIApplication([
  ('.*', DefaultHandler)
])