import venom

from app import app
from models import User


class ProfileHandler(venom.RequestHandler):
  def put(self):
    user = self.url.get('user')
    username, password, age = self.body.get('username', 'password', 'age')
    if username: user.username = username
    if password: user.password = password
    if age: user.age = age
    return user.save()


venom.ui(
app.PUT('/profile/:user', ProfileHandler).url({
  'user': venom.Parameters.Model(User)
}).body({
  'username': venom.Parameters.String(required=False),
  'password': venom.Parameters.String(required=False),
  'age': venom.Parameters.Integer(required=False)
}), 'ui-56389134')
