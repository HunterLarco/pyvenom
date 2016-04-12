import venom





class Tests(venom.Test):
  def setup(self):
    pass
  
  def test_thing(self):
    assert self.request('/serve', {
      'fileid': 'test'
    }) == {
      'success': True
    }





Tests.run()
