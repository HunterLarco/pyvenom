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



class TestHandlerGeneric(venom.RequestHandler):
  def get(self):
    # TODO
    # do thing

    # device = Device.getByKey(filekey)
    # return
    return venom.Protocols.JSONProtocol({
      'data': 123
    })






app = venom.Server(debug=True)



app.GET('/buckets/v1/serve/:filekey', TestHandlerGeneric).url({
  'filekey': venom.Parameters.Float()
})


app.POST('/buckets/v1/serve', TestHandlerGeneric).body({
  'otherthing': venom.Parameters.String(min=4, max=56),
  'thing': venom.Parameters.List({
    'test1': venom.Parameters.Int(),
    'test2': venom.Parameters.Int()
  }, min=2, max=5, required=False)
})
