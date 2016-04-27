import venom


app = venom.Application()



class TestModel(venom.Model):
  name = venom.Properties.String()

app.CRUD('/test', TestModel).domain.query({
  'thing': venom.Properties.String(required=True)
})


import user