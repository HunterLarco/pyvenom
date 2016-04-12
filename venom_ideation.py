import venom


class Property(object):
  pass


class PropertiedClass(type):
  def __new__(metaclass, name, parents, dct):
    cls = super(PropertiedClass, metaclass).__new__(metaclass, name, parents, dct)

    # Only works on indexed properties
    for key, value in dct.items():
      if isinstance(value, Property) and value.indexed:
        getKey = 'getBy{}'.format(key.capitalize())
        hasKey = 'hasBy{}'.format(key.capitalize())
        queryKey = 'queryBy{}'.format(key.capitalize())
        query = lambda val: cls.query(value == val)
        setattr(cls, queryKey, lambda val: query(val))
        setattr(cls, getKey  , lambda val: query(val).get())
        setattr(cls, hasKey  , lambda val: query(val).count() != 0)

    return cls


class Model(venom.Model):
  __metaclass__ = PropertiedClass


""" ASDFGHJKLKJHGFDSASDFGHJKLKJHGFDSASDFGHJKLKJHGFDSASDFGHJKLKJHGFDSASDFGHJKLKJHGFDSA """


class Protocol(venom.Protocols.Protocol):
  def __init__(self, headers=None, cookies=None):
    self.headers  = headers
    self.cookies  = cookies
    self.response = None

  def __enter__(self):
    self.response[headers] = self.headers
    self.response.cookies  = self.cookies

  def respond(self):
    raise NotImplemented()

  def __exit__(self):
    pass


class TestHandlerGeneric(venom.RequestHandler):
  def post(self):
    # json, multipart, etc...
    self.request.body.require
    self.request.body.maybe
    self.request.body.choose

    userid = 1234567890
    User.require(userid)
    User.maybe(userid)
    User.choose(userid1, userid2)

    file = self.request.multipart.require('file')
    key = venom.Buckets.save(file)

    return venom.Protocols.json({
      'key': key
    }, headers={
      'Content-Type': 'application/json'
    })


class TestHandler(venom.RequestHandler):
  def get(self, filekey):
    return venom.Buckets.serve(filekey)


app = venom(modules=[
  UserAuth
], routes=[
  ('/', TestHandlerGeneric),
  ('/:filekey/?', TestHandler)
], debug=True)













import venom



class DefaultHandler(venom.RequestHandler):
  def get(self):
    return venom.Protocols.JSONProtocol({
      'data': {
        'url': self.url,
        'query': self.query
      }
    })



app = venom.Server(debug=True)



router = app.Route('/buckets/v1/serve/:fileid', DefaultHandler)


router.GET.url({
  'fileid': venom.Parameters.Int(min=4, max=100)
}).query({
  'test': venom.Parameters.Float(required=False),
  'test2': venom.Parameters.List({
    'thing': venom.Parameters.Float()
  })
})# .body({
#   'items': venom.Parameters.List({
#     'title': venom.Parameters.String(min=4),
#     'description': venom.Parameters.String(min=4)
#   }, min=1)
# })