from helper import smart_assert, BasicTestCase
import venom

from google.appengine.ext import ndb


class ModelTest(BasicTestCase):
  def test_modelattribute_fixup(self):
    """
    ' Tests that a venom.Model subclass correctly assigns
    ' references on all ModelAttribute instances on that subclass
    ' to the parent model.
    '
    ' EXAMPLE
    '
    ' class Test(venom.Model):
    '   foo = venom.Properties.Property()
    '   bar = venom.Properties.Property()
    ' 
    ' This should set _name, _model, _entity on 'bar' and 'foo'
    ' (_entity only when instantiated)
    """
    
    class Test(venom.Model):
      foo = venom.Properties.Property()
      bar = venom.Properties.Property()
    
    smart_assert('foo', Test.foo._name).equals('[fail] prop._name == prop_name')
    smart_assert('bar', Test.bar._name).equals('[fail] prop._name == prop_name')
    smart_assert(Test, Test.foo._model).equals('[fail] prop._model == parent_model')
    smart_assert(Test, Test.bar._model).equals('[fail] prop._model == parent_model')
    
    test = Test()
    
    smart_assert(test, Test.foo._entity).equals('[fail] prop._entity == parent_entity')
    smart_assert(test, Test.bar._entity).equals('[fail] prop._entity == parent_entity')
  
  def test_property_setter_getter(self):
    class Test(venom.Model):
      foo = venom.Properties.Property()
      bar = venom.Properties.Property()
    
    test = Test()
    test.foo = 123
    assert test.foo == 123
    test.bar = 456
    test.foo = 789
    assert test.bar == 456
    assert test.foo == 789
  
  def test_populate_vs_from_stored(self):
    class TestProp(venom.Properties.Property):
      def _set_stored_value(self, entity, value):
        super(TestProp, self)._set_stored_value(entity, value // 2)
  
      def _get_stored_value(self, entity):
        return super(TestProp, self)._get_stored_value(entity) * 2
    
    class Test(venom.Model):
      foo = TestProp()
      bar = TestProp()
    
    test = Test(foo=123, bar=456)
    assert test.foo == 123
    assert test.bar == 456
    
    test = Test()
    test.populate(foo=123, bar=456)
    assert test.foo == 123
    assert test.bar == 456
    
    test = Test()
    test._populate_from_stored(foo=10, bar=26)
    assert test.foo == 5
    assert test.bar == 13
  
  def test_saving_and_updating(self):
    class TestProp(venom.Properties.Property):
      allowed_operators = venom.Properties.PropertyComparison.allowed_operators
      
      def _to_storage(self, value):
        return value * 2
  
      def _from_storage(self, value):
        return value // 2
      
      def to_datastore_property(self):
        return ndb.IntegerProperty
      
      def query_uses_datastore(self, operator, value):
        return True
    
    class Test(venom.Model):
      foo = TestProp()
      bar = TestProp()
      
      foo10 = venom.Query(foo == 10)
      foo34 = venom.Query(foo == 34)
    
    test = Test()
    test.foo = 10
    test.bar = 24
    test.save()
    
    entities = test.hybrid_model.query_by_datastore()
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.datastore_entity.get_entity().foo == 20
    assert entity.datastore_entity.get_entity().bar == 48
    
    entities = Test.foo10()
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.foo == 10
    assert entity.bar == 24
    
    entity.foo = 34
    entity.save()
    
    entities = Test.foo10()
    assert len(entities) == 0
    
    entities = Test.foo34()
    assert len(entities) == 1
    
    entity = entities[0]
    assert entity.foo == 34
    assert entity.bar == 24

  def test_schema(self):
    class User(venom.Model):
      username = venom.Properties.String()
      email = venom.Properties.String()
      age = venom.Properties.Float()
      password = venom.Properties.Password(min=5)
      bio = venom.Properties.String(max=None)

      login = venom.Query(email == venom.QP, password == venom.QP)
    
    def assert_schema(model, prop_name, datastore, indexed_datastore, search):
      assert model._schema[prop_name].datastore == datastore
      assert model._schema[prop_name].indexed_datastore == indexed_datastore
      assert model._schema[prop_name].search == search
    
    assert_schema(User, 'username', True, False, False)
    assert_schema(User, 'email'   , True, True , False)
    assert_schema(User, 'age'     , True, False, False)
    assert_schema(User, 'password', True, True , False)
    assert_schema(User, 'bio'     , True, False, False)
    
    User.bio_contains = venom.Query(User.bio.contains(venom.QP))
    User._init_class()
    
    assert_schema(User, 'username', True, False, False)
    assert_schema(User, 'email'   , True, True , False)
    assert_schema(User, 'age'     , True, False, False)
    assert_schema(User, 'password', True, True , False)
    assert_schema(User, 'bio'     , True, False, True )
    
    User.bio_contains = venom.Query(User.bio.contains(venom.QP), User.email == 'foo')
    User._init_class()
    
    assert_schema(User, 'username', True, False, False)
    assert_schema(User, 'email'   , True, True , True )
    assert_schema(User, 'age'     , True, False, False)
    assert_schema(User, 'password', True, True , False)
    assert_schema(User, 'bio'     , True, False, True )
    
    User.bio_contains = venom.Query(User.age > 5, User.email != 'foo')
    User._init_class()
    
    assert_schema(User, 'username', True, False, False)
    assert_schema(User, 'email'   , True, True , True )
    assert_schema(User, 'age'     , True, False, True )
    assert_schema(User, 'password', True, True , False)
    assert_schema(User, 'bio'     , True, False, False)
  
  def test_json(self):
    class User(venom.Model):
      username = venom.Properties.String()
      email = venom.Properties.String()
      age = venom.Properties.Float()
      password = venom.Properties.String(min=3)
      bio = venom.Properties.String(max=None)
    
    user = User(username='username', email='email', age=20, password='pass', bio='bio')
    json = user.__json__()
    
    assert json['username'] == 'username'
    assert json['email'] == 'email'
    assert json['age'] == 20
    assert json['password'] == 'pass'
    assert json['bio'] == 'bio'
    assert json['key'] == None
  
  def test_key_update(self):
    class User(venom.Model):
      username = venom.Properties.String()
      email = venom.Properties.String()
      age = venom.Properties.Float()
      password = venom.Properties.Password(min=3)
      bio = venom.Properties.String(max=None)
    
    user = User(username='username', email='email', age=20, password='pass', bio='bio')
    
    assert user.key == None
    user.save()
    assert user.key != None
    
    # check that key didn't change on a class level (for all instances)
    user = User()
    assert user.key == None
  
  def test_get(self):
    class User(venom.Model):
      username = venom.Properties.String()
      email = venom.Properties.String()
      age = venom.Properties.Float()
      password = venom.Properties.Password(min=3)
      bio = venom.Properties.String(max=None)
    
    user = User(username='username1')
    user.save()
    
    key1 = user.key
    assert User.get(key1).username == 'username1'
    
    user = User(username='username2')
    user.save()
    
    key2 = user.key
    assert User.get(key2).username == 'username2'
    
    users = User.get_multi([key1, key2])
    assert users[0].username == 'username1'
    assert users[1].username == 'username2'
