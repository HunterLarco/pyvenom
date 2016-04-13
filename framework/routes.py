import venom

from handlers import LoginHandler
from handlers import SignupHandler
from handlers import GroupsHandler
# from handlers import ProfileHandler

from models import User


app = venom.Application(version=1)


app.POST('/login', LoginHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String()
})

app.POST('/signup', SignupHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String(),
  'age': venom.Parameters.Integer(required=False, min=0, max=200)
})

# app.PUT('/profile/:userid', ProfileHandler).url({
#   'userid': venom.Parameters.Model(User)
# }).body({
#   'username': venom.Parameters.String(required=False),
#   'password': venom.Parameters.String(required=False),
#   'age': venom.Parameters.Integer(required=False)
# })

app.GET('/groups/:tag', GroupsHandler).url({
  'tag': venom.Parameters.String(choices=[
    'children', 'adults', 'teenagers', 'seniors', 'discounted'
  ])
})
