from helper import smart_assert, BasicTestCase
import venom

from google.appengine.ext import ndb


class TestDynamic(venom.internal.hybrid_model.DynamicModel):
  pass


class DynamicModelTest(BasicTestCase):
  def test_setting_properties(self):
    test = TestDynamic()
    with smart_assert.raises(AttributeError) as context:
      test.foo
    test.set('foo', 123, ndb.IntegerProperty)
    assert test.foo == 123
    test.foo = 456
    assert test.foo == 456
    assert 'foo' in test._properties
    assert test._properties['foo']._get_value(test) == 456
    test.set('bar', 789, ndb.IntegerProperty(indexed=True))
    assert test.bar == 789
  
  def test_saving_data(self):
    test = TestDynamic()
    test.set('foo', 123, ndb.IntegerProperty)
    test.foo = 789
    test.put()
    
    entity = TestDynamic.query().get()
    assert entity.foo == 789
    
    test = TestDynamic()
    test.set('foo', 123, ndb.IntegerProperty)
    test.set('bar', 456, ndb.IntegerProperty)
    test.put()
    
    entity = TestDynamic.query(test._properties['foo'] == 123).get()
    assert entity != None
    assert entity.foo == 123
    assert entity.bar == 456

  def test_updating_data(self):
    test = TestDynamic()
    test.set('foo', 123, ndb.IntegerProperty)
    test.put()
    
    entity = TestDynamic.query().get()
    entity.set('bar', 456, ndb.IntegerProperty)
    entity.foo = 789
    entity.put()
    
    entity = TestDynamic.query().get()
    assert entity.bar == 456
    assert entity.foo == 789

