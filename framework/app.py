import venom


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
