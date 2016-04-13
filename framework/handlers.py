import venom

from models import User


class LoginHandler(venom.RequestHandler):
  def post(self):
    username, password = self.body.get('username', 'password')
    users = User.login(username, password)
    if not users:
      self.throw(404)
      return { 'message': 'Credentials matched no known user' }
    return users[0]


class SignupHandler(venom.RequestHandler):
  def post(self):
    username, password, age = self.body.get('username', 'password', 'age')
    return User(username=username, password=password, age=age).save()


class GroupsHandler(venom.RequestHandler):
  def get(self):
    tag = self.url.get('tag')
    if tag == 'children':
      return { 'users': User.children() }
    elif tag == 'adults':
      return { 'users': User.adults() }
    elif tag == 'seniors':
      return { 'users': User.seniors() }
    elif tag == 'discounted':
      return { 'users': User.discounted() }
    return { 'users': User.teenagers() }


# class ProfileHandler(venom.RequestHandler):
#   def put(self):
#     pass