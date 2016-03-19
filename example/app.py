import venom


from google.appengine.ext import ndb
class TestModel(ndb.Model):
  test = ndb.StringProperty(indexed=True)


@venom.script
def query_models():
  print('Starting')
  query = TestModel.query(TestModel.test == '123').fetch(40)
  print('Done')
  return str(query)


@venom.script
def foo():
  return 'Hello Fero'


@venom.script
def bar():
  return 'Hello Jakey-poo!'


@venom.script
def generate_models():
  print('Starting')
  for i in range(1000):
    model = TestModel()
    model.test = '123'
    model.put()
  print('Done')


@venom.script
def analytics():
  """PURPOSE
  Total count of TestModel entities
RETURNS
  An integer count"""
  query = TestModel.query()
  count = query.count()
  print('TestModel Count: {}'.format(count))


import webapp2
app = webapp2.WSGIApplication([], debug=True)