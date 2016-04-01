import venom



class DefaultHandler(venom.RequestHandler):
  def get(self):
    return venom.Protocols.JSONProtocol({
      'data': {
        'url': self.url,
        'query': self.query
      }
    })



app = venom.Server(version=1.6, debug=True)



app.GET('serve/:fileid', DefaultHandler).url({
  'fileid': venom.Parameters.Int(min=4, max=100)
}).query({
  'test': venom.Parameters.Float()
  # 'test2': venom.Parameters.List({
    # 'thing': venom.Parameters.Float()
  # }, required=False)
})# .body({
#   'items': venom.Parameters.List({
#     'title': venom.Parameters.String(min=4),
#     'description': venom.Parameters.String(min=4)
#   }, min=1)
# })