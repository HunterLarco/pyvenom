import venom


@venom.script
def test_script():
  print('this is a test')
  print('lololol')
  return 2039438


import webapp2
app = webapp2.WSGIApplication([], debug=True)