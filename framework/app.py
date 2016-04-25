import venom


app = venom.Application()


class User(venom.Model):
  password = venom.Properties.Password(min=3, max=100, required=True)
  username = venom.Properties.String  (min=3, max=100, required=True, unique=True)
  email    = venom.Properties.String  (min=3, max=100, required=True, unique=True)
  
  
  by_username = venom.Query(username == venom.QP)
  by_email = venom.Query(email == venom.QP)
  
  login_by_username = venom.Query(by_username, password == venom.QP)
  login_by_email = venom.Query(by_email, password == venom.QP)

class SessionToken(venom.Model):
  token = venom.Properties.UUID()
  user = venom.Properties.Model(User)
  
  by_token = venom.Query(token == venom.QP)


class UserGenericHandler(venom.RequestHandler):
  def post(self):
    username, email, password = self.body.get('username', 'email', 'password')
    
    user = User(email=email, password=password, username=username).save()
    auth = SessionToken(user=user).save()

    return dict(user.__json__().items() + [('session_token', auth.token)])


class UserAuthHandler(venom.RequestHandler):
  def get(self):
    auth = self.headers.get('x-session')
    return auth.user


class UserAuthParameter(venom.Parameters.Model):
  def __init__(self, required=True):
    super(UserAuthParameter, self).__init__(SessionToken, required=required)
  
  def cast(self, key, value):
    value = super(venom.Parameters.Model, self).cast(key, value)
    results = SessionToken.by_token(value)
    if not results:
      return None
    return results[0]


app.POST('/users', UserGenericHandler).body({
  'username': User.username.to_route_parameter(),
  'email'   : User.email.to_route_parameter(),
  'password': User.password.to_route_parameter()
})

app.GET('/auth', UserAuthHandler).headers({
  'X-Session': UserAuthParameter()
})
