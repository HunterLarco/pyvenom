import venom

from app import app
from models import User


class SignupHandler(venom.RequestHandler):
  def post(self):
    username, password, age = self.body.get('username', 'password', 'age')
    return User(username=username, password=password, age=age).save()


venom.ui(
app.POST('/signup', SignupHandler).body({
  'username': venom.Parameters.String(),
  'password': venom.Parameters.String(),
  'age': venom.Parameters.Integer(required=False, min=0, max=200)
}), 'ui-3456789')
