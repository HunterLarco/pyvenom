import venom


app = venom.Application()


class HelloWorld(venom.RequestHandler):
  def get(self):
    return { 'message': 'Hello World!' }


app.GET('/helloworld', HelloWorld)
