import venom


app = venom.Application()


class User(venom.Model):
  age = venom.Properties.Integer(min=0)
  password = venom.Properties.Password(min=3, max=100, required=True)
  username = venom.Properties.String(min=3, max=100, required=True)
  
  by_username = venom.Query(username == venom.QP)


app.CRUD('/users', User)


class Thing(venom.RequestHandler):
  def get(self):
    pass


app.GET('/thing/:foo/list/:bar', Thing).url({
  'foo': venom.Parameters.String(min=1),
  'bar': venom.Parameters.String(min=1)
}).query({
  'query_int': venom.Parameters.Integer(min=1, required=False, choices=[1, 2, 3, 5, 8]),
  'query_float': venom.Parameters.Float(min=1, required=False)
}).headers({
  'X-Authorization': venom.Parameters.Model(User)
}).body({
  'numbers_list': venom.Parameters.List(
    venom.Parameters.Float(min=-10, max=10)
  , required=False),
  'integer': venom.Parameters.Integer(),
  'thing': {
    'foo': venom.Parameters.Float(),
    'bar': {
      'things': venom.Parameters.List({
        'name': venom.Parameters.String()
      })
    }
  }
})