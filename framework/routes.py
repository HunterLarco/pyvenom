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
}), 1000)


venom.ui(
version1.POST('/signup', SignupHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String(),
  'age': venom.Parameters.Integer(required=False, min=0, max=200)
}), 2000)

# right now this has an error where it created
# a new user instead of updating the old one
version1.PUT('/profile/:user', ProfileHandler).url({
  'user': venom.Parameters.Model(User)
}).body({
  'username': venom.Parameters.String(required=False),
  'password': venom.Parameters.String(required=False),
  'age': venom.Parameters.Integer(required=False)
})

version1.GET('/groups/:tag', GroupsHandler).url({
  'tag': venom.Parameters.String(choices=[
    'children', 'adults', 'teenagers', 'seniors', 'discounted'
  ])
})


version2 = venom.Application(version=2)


version2.GET('/helloworld', HelloWorldHandler)
