import venom


class DefaultHandler(venom.RequestHandler):
  def get(self):
    print('\n\n{}\n{}\n\n'.format(self.request.body, self.request.query))
    self.response.out.write('OK asd')
  
  def post(self):
    print('\n\n{}\n{}\n\n'.format(self.request.body, self.request.query))
    print(self.request.body.require('arr'))
    self.response.out.write('OK asd')


import webapp2
app = webapp2.WSGIApplication([
  ('.*', DefaultHandler)
], debug=True)