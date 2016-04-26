import venom
from app import app
from handlers import *
from models import *


__all__ = []


venom.ui(
app.POST('/users/signup', UserSignupHandler).body({
  'username': User.username.to_route_parameter(),
  'email'   : User.email.to_route_parameter(),
  'password': User.password.to_route_parameter()
}), 'ui-86491837498374')

venom.ui(
app.POST('/users/login', UserLoginHandler).body({
  'username': venom.Parameters.String(min=1, required=False),
  'email'   : venom.Parameters.String(min=1, required=False),
  'password': venom.Parameters.String(min=1, )
}), 'ui-92837423990493')

venom.ui(
app.GET('/users/me', UserAuthHandler).headers({
  'X-Session': UserAuthParameter()
}), 'ui-09876438920874')

venom.ui(
app.PUT('/users/me', UserAuthHandler).headers({
  'X-Session': UserAuthParameter()
}).body({
  'username': User.username.to_route_parameter(),
  'email'   : User.email.to_route_parameter(),
  'password': User.password.to_route_parameter()
}), 'ui-11283909844483')

venom.ui(
app.PATCH('/users/me', UserAuthHandler).headers({
  'X-Session': UserAuthParameter()
}).body({
  'username': venom.Parameters.String(min=3, max=100, required=False),
  'email'   : venom.Parameters.String(min=3, max=100, required=False),
  'password': venom.Parameters.String(min=3, max=100, required=False)
}), 'ui-26948370742073')

venom.ui(
app.DELETE('/users/me', UserAuthHandler).headers({
  'X-Session': UserAuthParameter()
}), 'ui-46789409723847')