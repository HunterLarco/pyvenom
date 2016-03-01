import venom


@venom.script
def test_script():
  print('this is a test')
  print('lololol')
  return 2039438


@venom.script
def hello():
  print('hello world')
  return '...completed'


import webapp2
app = webapp2.WSGIApplication([], debug=True)