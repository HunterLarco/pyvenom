import datetime


import venom


app = venom.Application()


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
