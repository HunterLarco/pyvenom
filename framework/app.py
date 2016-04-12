import venom


class Handler(venom.RequestHandler):
  def get(self):
    return { 'foo': 'bar' }


app = venom.Application()

app.GET('/test/:thing/and/:thing2', Handler).url({
  'thing': venom.Parameters.String(pattern='[^asd]+')
})
