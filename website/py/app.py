import webapp2


class DefaultHandler(webapp2.RequestHandler):
  def get(self):
    self.response.write('test py')


app = webapp2.WSGIApplication([
  ('.*', DefaultHandler)
])