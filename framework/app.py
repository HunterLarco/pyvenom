import venom
from google.appengine.ext import ndb

#
# class File(venom.Model):
#   fileid = venom.Properties.String()
#   author = venom.Properties.Integer(min=5)
#
#
# class MyFiles(venom.Query):
#   author = File.author
#

class File(ndb.Model):
  fileid = ndb.StringProperty(indexed=True)
  thing = ndb.IntegerProperty(indexed=True)
  
  def to_dict(self):
    return {
      'fileid': self.fileid,
      'thing': self.thing,
      'id': self.key.id()
    }


appv1 = venom.Application(version=1, debug=True, protocol=venom.Protocols.JSONProtocol)
appv2 = venom.Application(version=1.2, debug=True, protocol=venom.Protocols.JSONProtocol)

app = venom.VersionDispatcher(appv1, appv2)




class FileHandlerV1(venom.RequestHandler):
  def get(self):
    return { 'file': self.url.get('fileid').to_dict() }
  
  def post(self):
    fileid, thing = self.body.get('fileid', 'thing')
    File(fileid=fileid, thing=thing).put()


class DefaultHandlerV2(venom.RequestHandler):
  def get(self):
    return {
      'hello': 'world'
    }




appv1.GET('/serve/:fileid', FileHandlerV1).url({
  'fileid': venom.Parameters.Model(File, key='fileid', type=venom.Parameters.String())
})

appv1.POST('/serve', FileHandlerV1).body({
  'fileid': venom.Parameters.String(min=5),
  'thing': venom.Parameters.Int()
})

appv1.GET('/serve', FileHandlerV1)


# appv1.CRUD('/files', File)






appv2.GET('/serve/', DefaultHandlerV2)
