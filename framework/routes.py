import venom

from handlers import LoginHandler
from handlers import SignupHandler
from handlers import GroupsHandler
from handlers import ProfileHandler
from handlers import HelloWorldHandler

from models import User


version1 = venom.Application(version=1)


venom.ui(
version1.POST('/login', LoginHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String()
}), 'ui-0234789')


venom.ui(
version1.POST('/signup', SignupHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String(),
  'age': venom.Parameters.Integer(required=False, min=0, max=200)
}), 'ui-3456789')

# right now this has an error where it created
# a new user instead of updating the old one
venom.ui(
version1.PUT('/profile/:user', ProfileHandler).url({
  'user': venom.Parameters.Model(User)
}).body({
  'username': venom.Parameters.String(required=False),
  'password': venom.Parameters.String(required=False),
  'age': venom.Parameters.Integer(required=False)
}), 'ui-56389134')

version1.GET('/groups/:tag', GroupsHandler).url({
  'tag': venom.Parameters.String(choices=[
    'children', 'adults', 'teenagers', 'seniors', 'discounted'
  ])
})

venom.ui(
version1.GET('/crazything/:foo/:bar', GroupsHandler).url({
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


version2 = venom.Application(version=2)


version2.GET('/helloworld', HelloWorldHandler)
