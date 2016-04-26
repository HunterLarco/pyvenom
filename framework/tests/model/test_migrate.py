from helper import smart_assert, BasicTestCase
import venom

from google.appengine.ext import ndb


class MigrationTests(BasicTestCase):
  def test_migration_works(self):
    class Test(venom.Model):
      auto_migrate_in_dev = False
      
      foo = venom.Properties.String()
      bar = venom.Properties.String()
      
      matches = venom.Query(foo == 'foo', bar == 'bar')
    
    Test(foo='foo', bar='bar').save()
    assert len(Test.matches()) == 1
    
    class Test(venom.Model):
      auto_migrate_in_dev = False
      
      foo = venom.Properties.String(max=None)
      bar = venom.Properties.String()
      
      matches = venom.Query(foo == 'foo', bar == 'bar')
    
    assert len(Test.matches()) == 0
    
    venom.migrate.Migration().run()
    
    assert len(Test.matches()) == 1
    
  