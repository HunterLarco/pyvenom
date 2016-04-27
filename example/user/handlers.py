import venom
import datetime
from models import *


__all__ = ['UserSignupHandler', 'UserLoginHandler', 'UserAuthHandler']


class UserSignupHandler(venom.RequestHandler):
  def post(self):
    username, email, password = self.body.get('username', 'email', 'password')
    
    user = User(email=email, password=password, username=username).save()
    auth = SessionToken(user=user).save()

    return dict(user.__json__().items() + [('session_token', auth.token)])


class UserLoginHandler(venom.RequestHandler):
  def post(self):
    username, email, password = self.body.get('username', 'email', 'password')
    
    if not username and not email:
      raise venom.Parameters.ParameterValidationFailed(
        "'username' or 'email' field is required, but both were missing"
      )
    
    user = None
    if username:
      user = User.login_by_username(username, password).get()
    elif email:
      user = User.login_by_email(email, password).get()
    
    if not user:
      raise venom.Parameters.ParameterValidationFailed(
        "No user exists matching the given credentials"
      )
    
    user.last_login = datetime.datetime.now()
    auth = SessionToken(user=user)
    venom.Model.save_multi([user, auth])
    
    return dict(user.__json__().items() + [('session_token', auth.token)])


class UserAuthHandler(venom.RequestHandler):
  def get(self):
    user = self.headers.get('x-session')
    return user
  
  def put(self):
    username, email, password = self.body.get('username', 'email', 'password')
    user = self.headers.get('x-session')
    user.populate(username=username, email=email, password=password)
    return user.save()
  
  def patch(self):
    username, email, password = self.body.get('username', 'email', 'password')
    user = self.headers.get('x-session')
    if username: user.username = username
    if email   : user.email    = email
    if password: user.password = password
    return user.save()
  
  def delete(self):
    user = self.headers.get('x-session')
    user.delete()
