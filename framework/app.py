import venom


app = venom.Application()


class User(venom.Model):
  age = venom.Properties.Integer(min=0)
  password = venom.Properties.Password(min=3, max=100)
  username = venom.Properties.String(min=3, max=100)
  
  by_username = venom.Query(username == venom.QP('username'))


app.CRUD('/users', User)