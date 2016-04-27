from helper import smart_assert, BasicTestCase
from venom.internal.hybrid_model import HybridModel
import venom

from google.appengine.ext import ndb
from google.appengine.api import search


class TestDynamicModel(HybridModel):
  pass


class HybridModelTests(BasicTestCase):
  def test_put(self):
    entity = TestDynamicModel()
    entity.set('username', 'test_account', ndb.StringProperty)
    entity.set('username', 'test_account', search.TextField)
    
    assert entity.datastore_entity.get_entity() == None
    assert entity.search_document.get_document() == None
    
    assert entity.datastore_has_diff() == True
    assert entity.document_has_diff() == True
    
    entity.put()
    
    assert entity.datastore_entity.get_entity() != None
    assert entity.search_document.get_document() != None
    
    assert entity.datastore_has_diff() == False
    assert entity.document_has_diff() == False
    
    assert entity.datastore_entity.get_entity().username == 'test_account'
    assert len(entity.search_document.get_document().fields) == 1
    
    document_id = entity.search_document.document_id
    entity = ndb.Key(TestDynamicModel.kind, int(document_id)).get()
    assert entity != None
  
  def test_update(self):
    entity = TestDynamicModel()
    
    assert entity.datastore_has_diff() == True
    assert entity.document_has_diff() == False
    
    entity.put()
    
    assert entity.datastore_has_diff() == False
    assert entity.document_has_diff() == False
    
    entity.set('username', 'test_account', ndb.StringProperty)
    
    assert entity.datastore_has_diff() == True
    assert entity.document_has_diff() == False
    
    entity.set('username', 'test_account', search.TextField)
    
    assert entity.datastore_has_diff() == True
    assert entity.document_has_diff() == True
    
    entity.put()
    
    assert entity.datastore_has_diff() == False
    assert entity.document_has_diff() == False
  
  def test_put_multi(self):
    foo = TestDynamicModel()
    bar = TestDynamicModel()
    baz = TestDynamicModel()
    
    bar.put()
    
    assert foo.datastore_has_diff() == True
    assert foo.document_has_diff() == False
    assert bar.datastore_has_diff() == False
    assert bar.document_has_diff() == False
    assert baz.datastore_has_diff() == True
    assert baz.document_has_diff() == False
    
    TestDynamicModel.put_multi([ foo, bar, baz ])
    
    assert foo.datastore_has_diff() == False
    assert foo.document_has_diff() == False
    assert bar.datastore_has_diff() == False
    assert bar.document_has_diff() == False
    assert baz.datastore_has_diff() == False
    assert baz.document_has_diff() == False
  
  def test_get(self):
    entity = TestDynamicModel()
    entity.set('username', 'test_account', ndb.StringProperty)
    entity.set('username', 'test_account', search.TextField)
    entity.put()
    
    document_id = entity.search_document.document_id
    entity_key = entity.datastore_entity.entity_key
    
    assert document_id != None
    assert entity_key != None
    
    assert TestDynamicModel.get(entity_key) != None
    assert TestDynamicModel.get(document_id) != None
    
    assert TestDynamicModel.get(ndb.Key('foo', 'bar')) == None
    assert TestDynamicModel.get('foobar') == None
  
  def test_get_multi(self):
    foo = TestDynamicModel()
    foo.set('name', 'foo', ndb.StringProperty)
    foo.set('name', 'foo', search.TextField)
    
    bar = TestDynamicModel()
    bar.set('name', 'bar', ndb.StringProperty)
    bar.set('name', 'bar', search.TextField)
    
    TestDynamicModel.put_multi([foo, bar])
    keys = [foo.datastore_entity.entity_key, foo.search_document.document_id, 'test']
    
    foo, bar, baz = TestDynamicModel.get_multi(keys)
    
    assert foo.datastore_entity.get_entity().name == 'foo'
    assert bar.datastore_entity.get_entity().name == 'foo'
    assert baz == None
    
    
    
