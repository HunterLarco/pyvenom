from helper import smart_assert, BasicTestCase
import venom

from google.appengine.ext import ndb
from google.appengine.api import search


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


class TestHybrid(venom.internal.hybrid_model.HybridModel):
  default_indexed = True


class HybridModelTest(BasicTestCase):
  def test_metaclass(self):
    assert TestHybrid.kind == 'TestHybrid'
    assert TestHybrid.model
    assert TestHybrid.index
  
  def test_queries(self):
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.set('bar', 'baz', ndb.StringProperty)
    entity.set('baz', 456, search.NumberField)
    entity.put()
    
    # query by search on mutual property
    entities = TestHybrid.query_by_search('foo = 123')
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.datastore_entity.get_entity().foo == 123
    assert entity.datastore_entity.get_entity().bar == 'baz'
    
    # query by search on ndb only property
    entities = TestHybrid.query_by_search('bar = baz')
    assert len(entities) == 0
    
    # query by ndb on ndb only property
    entities = TestHybrid.query_by_datastore(ndb.GenericProperty('bar') == 'baz')
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.datastore_entity.get_entity().foo == 123
    assert entity.datastore_entity.get_entity().bar == 'baz'
    
    # query by search on search only property
    entities = TestHybrid.query_by_search('baz = 456')
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.datastore_entity.get_entity().foo == 123
    assert entity.datastore_entity.get_entity().bar == 'baz'
    
    # since baz exists only on search documents
    # it cannot be found on a returned entity from the ndb
    with smart_assert.raises(AttributeError) as context:
      entity.datastore_entity.get_entity().baz
    
    # query by ndb on search only property
    entities = TestHybrid.query_by_datastore(ndb.GenericProperty('baz') == 456)
    assert len(entities) == 0
  
  def test_saving_data(self):
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.set('bar', 'baz', ndb.StringProperty)
    entity.put()
    
    entities = TestHybrid.query_by_datastore()
    assert len(entities) == 1

  def test_updating_data(self):
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.set('bar', 'baz', ndb.StringProperty)
    entity.put()
    
    entity = TestHybrid(entity=entity.datastore_entity.get_entity())
    entity.set('baz', 456, ndb.IntegerProperty)
    entity.set('baz', 456, search.NumberField)
    entity.set('bar', 'updated', ndb.StringProperty)
    entity.put()
    
    entities = TestHybrid.query_by_datastore()
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.datastore_entity.get_entity().baz == 456
    assert entity.datastore_entity.get_entity().bar == 'updated'
    
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.set('bar', 'baz', ndb.StringProperty)
    ndb_entity = entity.put()
    
    entities = TestHybrid.query_by_datastore()
    assert len(entities) == 2
  
  def test_deleting_data(self):
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.set('bar', 'baz', ndb.StringProperty)
    entity.put()
    
    entities = TestHybrid.query_by_datastore()
    assert len(entities) == 1
    
    entity.delete()
    
    entities = TestHybrid.query_by_datastore()
    assert len(entities) == 0

  def test_get(self):
    entity = TestHybrid()
    entity.set('foo', 123, ndb.IntegerProperty)
    entity.set('foo', 123, search.NumberField)
    entity.put()
    
    key1 = entity.datastore_entity.entity_key
    doc1 = entity.search_document.document_id
    
    entity = TestHybrid.get(key1)
    assert entity.datastore_entity.get_entity().foo == 123
    entity = TestHybrid.get(doc1)
    assert entity.datastore_entity.get_entity().foo == 123
    
    entity = TestHybrid()
    entity.set('foo', 456, ndb.IntegerProperty)
    entity.set('foo', 456, search.NumberField)
    entity.put()
    
    key2 = entity.datastore_entity.entity_key
    doc2 = entity.search_document.document_id
    
    entities = TestHybrid.get_multi([key1, key2])
    assert entities[0].datastore_entity.get_entity().foo == 123
    assert entities[1].datastore_entity.get_entity().foo == 456
    
    entities = TestHybrid.get_multi([doc1, doc2])
    assert entities[0].datastore_entity.get_entity().foo == 123
    assert entities[1].datastore_entity.get_entity().foo == 456
    