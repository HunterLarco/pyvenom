import venom


class User(venom.Model):
  username = venom.Properties.String  (max=20)
  age      = venom.Properties.Integer (min=0, default=0)
  password = venom.Properties.Password(max=20, hidden=True)
  
  adults      = venom.Query(age >= 18)
  children    = venom.Query(age < 18)
  teenagers   = venom.Query(children, age >= 13)
  seniors     = venom.Query(age >= 70)
  discounted  = venom.Query(venom.OR(children, seniors))
  
  login       = venom.Query(username, password)
