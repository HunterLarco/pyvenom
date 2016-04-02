import venom


appv1 = venom.Application(version=1, debug=True, protocol=venom.Protocols.JSONProtocol)
appv2 = venom.Application(version=1.2, debug=True, protocol=venom.Protocols.JSONProtocol)

app = venom.VersionDispatcher(appv1, appv2)



class DefaultHandlerV1(venom.RequestHandler):
  def post(self):
    return {
      'given_body': self.body,
      'given_url': self.url
    }


class DefaultHandlerV2(venom.RequestHandler):
  def get(self):
    return {
      'hello': 'world'
    }



appv1.POST('/serve/:fileid', DefaultHandlerV1).url({
  'fileid': venom.Parameters.Int(min=1)
}).body({
  'numbers': venom.Parameters.List(venom.Parameters.Int()),
  'test_dict': venom.Parameters.List({
    'test': venom.Parameters.String()
  }, min=2)
})
appv2.GET('/serve/', DefaultHandlerV2)




"""import venom



class DefaultHandler(venom.RequestHandler):
  def get(self):
    return venom.Protocols.JSONProtocol({
      'data': {
        'url': self.url,
        'query': self.query
      }
    })



appv1 = venom.Application(version=1, debug=True)
appv2 = venom.Application(version=2, debug=True)

# app = venom.serve(appv1, appv2)



appv1.GET('serve/:fileid', DefaultHandler).url({
  'fileid': venom.Parameters.Int(min=4, max=100)
}).query({
  'test': venom.Parameters.Float()
})

appv2.GET('serve/:fileid', DefaultHandler).url({
  'fileid': venom.Parameters.Int(min=1, max=10)
})"""