import venom


class User(venom.Model):
  # username = venom.StringProperty(unique=True)
  username = venom.Properties.String()
  password = venom.Properties.String()
  
  username_hunter = venom.Query(username == 'hunter')


class Handler(venom.RequestHandler):
  def post(self):
    return {
      'value': self.body.get('bar')
    }


appv1 = venom.Application(version=1)
appv2 = venom.Application(version=1.2)

app = venom.VersionDispatch(appv1, appv2)

appv1.POST('/test/:thing/and/:thing2', Handler).url({
  'thing': venom.Parameters.String(pattern='[^asd]+')
}).headers({
  'Foo': venom.Parameters.Float(min=5)
})

# appv1.serve('/hunter', User.username_hunter)




class QueryHandler(venom.RequestHandler):
  def get(self):
    return { 'query': User.username_hunter() }
  
  def post(self):
    username, password = self.body.get('username', 'password')
    return { 'user': User(username=username, password=password).save() }


appv1.GET('/hunter', QueryHandler)

appv1.POST('/hunter', QueryHandler).body({
  'username': venom.Parameters.String(min=3),
  'password': venom.Parameters.String(min=5)
})
