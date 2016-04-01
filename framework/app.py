import venom



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
})