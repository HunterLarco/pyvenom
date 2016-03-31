import venom
#
#
#
# class MeshProtocol(venom.Protocol):
#   pass
#
#
#
# class DeviceMigration(venom.Migration):
#   pass
#
#
#
# class Device(venom.Model):
#   key = venom.Models.UniqueKey(indexed=True, required=True)
#   name = venom.Models.String(migration=DeviceMigration)




class ServerHandler(venom.RequestHandler):
  def get(self):
    return venom.Protocols.XMLProtocol({
      'data': {
        'query': self.query,
        'url': self.url,
        'body': self.body
      }
    }, headers={
      'test-header': '123'
    })



app = venom.Server(debug=True)




app.GET('/buckets/v1/serve/:fileid', ServerHandler).url({
  'fileid': venom.Parameters.Int(min=0)
}).query({
  'test': venom.Parameters.Float(min=0, max=4)
})# .body({
#   'thing': venom.Parameters.List({
#     'test1': venom.Parameters.String(choices=['abc', 'dba'])
#   }, required=False)
# }, protocol=XMLProtocol)