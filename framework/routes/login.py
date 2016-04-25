import venom

from app import app
from models import User


class LoginHandler(venom.RequestHandler):
  def post(self):
    username, password = self.body.get('username', 'password')
    users = User.login(username, password)
    if not users:
      self.throw(404)
      return { 'message': 'Credentials matched no known user' }
    return users[0]


venom.ui(
app.POST('/login', LoginHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String()
}), 'ui-0234789')
