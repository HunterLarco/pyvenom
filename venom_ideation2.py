import venom




appv1 = venom.Application(version=1, debug=True, protocol=venom.Protocols.JSONProtocol)
appv2 = venom.Application(version=1.2, debug=True, protocol=venom.Protocols.JSONProtocol)

app = venom.VersionDispatcher(appv1, appv2)





class File(venom.Model):
  file     = venom.Properties.File()
  filename = venom.Properties.String(min=1)
  user     = venom.Properties.Reference()


class User(venom.Model):
  name = venom.Properties.String()
  age  = venom.Properties.Int(min=18)





class FileHandlerV1(venom.RequestHandler):
  def get(self):
    return { 'file': self.url.get('fileid').to_dict() }
  
  def post(self):
    fileid, thing, user = self.body.get('fileid', 'thing', 'user')
    File(fileid=fileid, thing=thing, user=user).put()





route1 = appv1.GET('/serve/:fileid', FileHandlerV1).url({
  'fileid': venom.Parameters.Model(File)
})

appv1.POST('/serve', FileHandlerV1).body({
  'file': venom.Parameters.FileUpload(),
  'filename': venom.Parameters.String(min=1),
  'user': venom.Parameters.Model(User)
})


appv1.CRUD('/files', File)
