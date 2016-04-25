import venom

from app import app
from models import User


class EmptyHandler(venom.RequestHandler):
  def get(self):
    pass


venom.ui(
app.GET('/crazything/:foo/:bar', EmptyHandler).url({
  'foo': venom.Parameters.String(),
  'bar': venom.Parameters.Float(min=7)
}).headers({
  'X-Authorization': venom.Parameters.Model(User),
  'user-agent': venom.Parameters.String()
}).query({
  'count': venom.Parameters.Integer(),
  'buzzword': venom.Parameters.String()
}).body({
  'favorite_things': venom.Parameters.List({
    'name': venom.Parameters.String(),
    'age': venom.Parameters.Float(),
    'random_json': venom.Parameters.Dict({
      'my_str': venom.Parameters.String(),
      'my_int_list': venom.Parameters.List(
        venom.Parameters.Integer()
      )
    })
  }),
  'date': venom.Parameters.Integer(),
  'random_string': venom.Parameters.String()
}), 'ui-93486109347')
