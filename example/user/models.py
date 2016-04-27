import venom
import datetime


__all__ = ['User', 'SessionToken', 'UserAuthParameter', 'UserAuthProperty']


class User(venom.Model):
  password = venom.Properties.Password(min=3, max=100, required=True)
  username = venom.Properties.String  (min=3, max=100, required=True, unique=True)
  email    = venom.Properties.String  (min=3, max=100, required=True, unique=True)
  
  created      = venom.Properties.DateTime(set_on_creation=True)
  last_updated = venom.Properties.DateTime(set_on_update=True)
  last_login   = venom.Properties.DateTime()
  
  by_username = venom.Query(username == venom.QP)
  by_email = venom.Query(email == venom.QP)
  
  login_by_username = venom.Query(by_username, password == venom.QP)
  login_by_email = venom.Query(by_email, password == venom.QP)

class SessionToken(venom.Model):
  expiration_hours = 48
  
  def __init__(self, *args, **kwargs):
    now = datetime.datetime.now()
    timedelta = datetime.timedelta(hours=self.expiration_hours)
    expiration = now + timedelta
    kwargs['expiration'] = expiration
    super(SessionToken, self).__init__(*args, **kwargs)
  
  token      = venom.Properties.UUID(required=True)
  user       = venom.Properties.Model(User, required=True)
  expiration = venom.Properties.DateTime(required=True)
  
  find_auth = venom.Query(token == venom.QP, expiration > venom.QP)


class UserAuthParameter(venom.Parameters.Model):
  def __init__(self, required=True):
    super(UserAuthParameter, self).__init__(SessionToken, required=required)
  
  def cast(self, key, value):
    value = super(venom.Parameters.Model, self).cast(key, value)
    results = SessionToken.find_auth(value, datetime.datetime.now())
    if not results:
      return None
    result = results[0]
    return result.user


class UserAuthProperty(venom.Properties.Model):
  def __init__(self):
    super(UserAuthProperty, self).__init__(User, required=True)
  
  def to_route_parameter(self):
    return UserAuthParameter()
