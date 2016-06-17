import venom


foobar = venom.Enum('foo bar baz')
foobar.bar


@venom.Blueprint('''
MESSAGE request:
  required string username
  required int userid
  required bool requires_adult
  optional uint age [default = 1]
    enforce age > 0
    enforce age < 100
    enforce age > 18 when requires_adult is true
        or environment.testing

MESSAGE response:
  required long longitude
  required long latitude

REQUEST:
  encoding [json, xml, rpc]
  container [location_request]

RESPONSE:
  encoding [auto]
  container [location_response]
''')
class GetMyLocation(venom.Endpoint):
  def execute(self, request):
    username = request.username
    userid = request.userid
    age = request.age
    
    response = {
      'longitude': 45L,
      'latitude': 3L
    }
    
    availability_response = availability_service.do(response)
    if not availability_response.is_available:
      return {}
    
    return {
      'longitude': 45L,
      'latitude': 3L
    }


location_service = venom.MicroService('LocationService')
location_service.serve('/getMyLocation', GetMyLocation)


central_dispatch = venom.CommandCenter(config='venom.config')
'''
CONFIG:
  visibility [public]
  prefix [staging]
'''
central_dispatch.install(location_service)
central_dispatch.install(auth_service)
central_dispatch.install(availability_service)

central_dispatch.start()
