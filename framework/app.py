import venom


class Test2(venom.WSGIEntryPoint):
  def dispatch(self, request, response, error):
    response.write('test2')


class Test(venom.WSGIEntryPoint):
  def dispatch(self, request, response, error):
    return Test2()


app = Test()