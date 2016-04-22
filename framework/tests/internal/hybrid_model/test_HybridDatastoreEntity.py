from helper import smart_assert, BasicTestCase
from venom.internal.hybrid_model import HybridDatastoreEntity
from venom.internal.hybrid_model import DatastorePropertyContainer
from venom.internal.hybrid_model import DynamicModel
import venom

from google.appengine.ext import ndb


class TestDynamicModel(DynamicModel):
  pass


class HybridDatastoreEntityTests(BasicTestCase):
  model = TestDynamicModel
  default_properties = [
    DatastorePropertyContainer(ndb.StringProperty, 'username', 'test_account'),
    DatastorePropertyContainer(ndb.FloatProperty, 'age', 20.3)
  ]
  new_properties = [
    DatastorePropertyContainer(ndb.FloatProperty, 'age', 89)
  ]
  changed_properties = [
    DatastorePropertyContainer(ndb.StringProperty, 'username', 'updated'),
    DatastorePropertyContainer(ndb.FloatProperty, 'age', 12)
  ]
  
  def _create_datastore_entity(self, properties=None):
    properties = properties if properties else self.default_properties
    entity = TestDynamicModel()
    for prop, name, value in properties:
      entity.set(name, value, prop)
    entity.put()
    return entity
  
  def test_given_no_entity(self):
    hybridentity = HybridDatastoreEntity(self.model)
    
    assert hybridentity.has_diff(self.default_properties) == True
    
    assert hybridentity._loaded_entity == False
    assert hybridentity.get_entity() == None
    
    update_entity = hybridentity.get_update_entity(self.default_properties)
    assert update_entity != None
    assert update_entity.key == None
    
    update_entity.put()
    hybridentity.register_update(update_entity)
    
    assert hybridentity._loaded_entity == True
    assert hybridentity.get_entity() != None
    
    assert hybridentity.has_diff(self.default_properties) == False
  
  def test_given_entity(self):
    entity = self._create_datastore_entity()
    hybridentity = HybridDatastoreEntity(self.model, entity=entity)
    
    assert hybridentity._loaded_entity == True
    assert hybridentity.get_entity() != None
    
    assert hybridentity.has_diff(self.default_properties) == False
    assert hybridentity.has_diff(self.new_properties) == True
    assert hybridentity.has_diff(self.changed_properties) == True
    
    update_entity = hybridentity.get_update_entity(self.new_properties)
    assert update_entity != None
    assert update_entity.key == hybridentity.entity_key
    
    update_entity.put()
    hybridentity.register_update(update_entity)
    
    assert hybridentity._loaded_entity == True
    assert hybridentity.get_entity() != None
    assert hybridentity.has_diff(self.default_properties) == True
    assert hybridentity.has_diff(self.new_properties) == False
  
  def test_given_entity_key(self):
    entity = self._create_datastore_entity()
    hybridentity = HybridDatastoreEntity(self.model, entity_key=entity.key)
    
    assert hybridentity._loaded_entity == False
    assert hybridentity.get_entity() != None
    assert hybridentity._loaded_entity == True
    
    hybridsearch = HybridDatastoreEntity(self.model, entity_key=entity.key)
    
    assert hybridentity.has_diff(self.default_properties) == False
    assert hybridentity.has_diff(self.new_properties) == True
    assert hybridentity.has_diff(self.changed_properties) == True
  
  def test_given_bad_entity_key(self):
    hybridentity = HybridDatastoreEntity(self.model, entity_key='foobar')
    hybridentity = HybridDatastoreEntity(self.model, entity_key=ndb.Key('foo', 'bar'))
  
    assert hybridentity._loaded_entity == False
    assert hybridentity.get_entity() == None
    assert hybridentity._loaded_entity == True
    
    assert hybridentity.has_diff(self.default_properties) == True
    assert hybridentity.has_diff(self.new_properties) == True
    assert hybridentity.has_diff(self.changed_properties) == True  
    