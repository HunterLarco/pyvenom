import venom


app = venom.Application(version=1, debug=True, protocol=venom.Protocols.JSONProtocol)


# migration
class User(venom.Model):
  username  = venom.Properties.String(min=1)
  lastname  = venom.Properties.String(min=1)
  firstname = venom.Properties.String(min=1)
  age       = venom.Properties.Int(min=0)
  location  = venom.Properties.Geopoint()
  
  # upload = venom.Properties.ImageUpload()
  
  adults = venom.Query(age >= 18)
  children = venom.Query(age < 18)
  
  byage = venom.QueryString(age, username)
  
  olderthan = venom.Query(age > venom.QueryProperty)
  nearme = venom.Query(location.distance(venom.QueryProperty('latlon')) < 1000)
  

app.serve('/users/adults', User.adults)


app.CRUD('/users', User)


User.nearme(latlong=(45, 78))
User.olderthan(21)


class QueryHander(venom.RequestHandler):
  def get(self):
    choice = self.request.url.get('agetype')
    if choice == 'adult':
      return { 'query': User.adults.to_dict() }
    return { 'query': User.children.to_dict() }


app.GET('/users/:agetype', QueryHander).url({
  'agetype': venom.Parameters.String(choices=['adult', 'child'])
}).body({
  'filename': venom.Parameter.String(min=3, max=100, characters='abcdefghijklmnop'),
  'file': venom.Parameter.Integer(min=0),
  'nested': {
    'foo': venom.Parameter.Float()
  },
  # children
  # properties
  # template
  'nested2': venom.Parameter.Dict({
    'foo': venom.Parameter.Float()
  }, required=False),
  'email': vneom.Parameter.String(pattern='.*', min=2)
}).headers({
  'X-Authorization': venom.Parameter.Integer()
})
