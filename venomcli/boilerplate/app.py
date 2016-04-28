import venom


app = venom.Application()


class HelloWorld(venom.RequestHandler):
  def get(self):
    return { 'message': 'Hello World!' }


venom.ui(
app.GET('/helloworld', HelloWorld)
, 'ui-374891883476389473943')
