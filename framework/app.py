import venom


class Handler(venom.RequestHandler):
  def post(self):
    return {
      'value': self.body.get('bar')
    }


app = venom.Application()

app.POST('/test/:thing/and/:thing2', Handler).url({
  'thing': venom.Parameters.String(pattern='[^asd]+')
}).headers({
  'Foo': venom.Parameters.Float(min=5)
}).body({
  'bar': venom.Parameters.Float(max=4)
})
