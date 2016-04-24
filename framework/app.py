import venom


app = venom.Application()


class User(venom.Model):
  username = venom.Properties.String  (max=20)
  age      = venom.Properties.Integer (min=0)
  password = venom.Properties.Password(max=20)


app.CRUD('/users', User)