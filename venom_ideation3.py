import venom


app = venom.Application(version=1, debug=True, protocol=venom.Protocols.JSONProtocol)


class User(venom.Model):
  username = venom.Properties.String(min=1)
  lastname = venom.Properties.String(min=1)
  firstname = venom.Properties.String(min=1)
  age  = venom.Properties.Int(min=0)
  
  adults = venom.Query(age >= 18)
  children = venom.Query(age < 18)
  

app.serve('/users/adults', User.adults)


app.CRUD('/users', User)


class QueryHander(venom.RequestHandler):
  def get(self):
    choice = self.request.url.get('agetype')
    if choice == 'adult':
      return { 'query': User.adults.to_dict() }
    return { 'query': User.children.to_dict() }


app.GET('/users/:agetype', QueryHander).url({
  'agetype': venom.Parameters.String(choices=['adult', 'child'])
})
