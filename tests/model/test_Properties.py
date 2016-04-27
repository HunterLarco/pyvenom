from google.appengine.ext import ndb
from google.appengine.api import search
from helper import smart_assert, BasicTestCase
import venom


class BasePropertyTest(BasicTestCase):
  def test_model_property(self):
    class InnerModel(venom.Model):
      name = venom.Properties.String()
    
    class TestModel(venom.Model):
      inner = venom.Properties.Model(InnerModel)
    
    inner = InnerModel(name='test').save()
    test = TestModel(inner=inner).save()
    
    # test that model is stored internally (not key)
    assert test.inner == inner
    assert test._values['inner'] == inner
    
    test = TestModel.get(test.key)
    
    # test that key only is loaded from db
    assert test._values['inner'] == inner.key
    
    # test lazy loaded model upon key access
    assert isinstance(test.inner, InnerModel)
    assert test._values['inner'] != inner.key
  
  def test_password_property(self):
    self.__test_string_property(venom.Properties.Password)
    
    class ModelStub(venom.Model):
      prop = venom.Properties.Password()
    
    model = ModelStub()
    model.prop = 'test'
    
    # stored as hash
    assert model.prop != 'test'
    assert len(model.prop) == 64
    
    # to storage changes to hash but from storage doesn't
    assert ModelStub.prop._to_storage('test') != 'test'
    assert ModelStub.prop._from_storage('test') == 'test'
    
    # get stored value doesn't re-hash
    assert ModelStub.prop._get_stored_value(model) == model.prop
  
  def test_string_property(self):
    self.__test_string_property(venom.Properties.String)
  
  def __test_string_property(self, prop_cls):
    prop = prop_cls(min=2, max=8, choices=['foo', 'bar', 'baz'], required=True, characters='fobar')
    
    assert prop.min == 2
    assert prop.max == 8
    assert prop.choices == ['foo', 'bar', 'baz']
    assert prop.required == True
    assert prop.characters == 'fobar'
    
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None, 'a')
      prop.validate(None, 'foobar')
      prop.validate(None, 'baz')
      prop.validate(None, 'aaaaaaaaa')
    with smart_assert.raises() as context:
      prop.validate(None, 'foo')
      prop.validate(None, u'bar')
      
    assert isinstance(prop._from_storage(unicode('bar')), str)
  
  def test_float_property(self):
    prop = venom.Properties.Float(min=2, max=8, choices=[1, 3.5, 4, 9], required=True)
    
    assert prop.min == 2
    assert prop.max == 8
    assert prop.choices == [1, 3.5, 4, 9]
    assert prop.required == True
    
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None, 1)
      prop.validate(None, 3)
      prop.validate(None, 9)
    with smart_assert.raises() as context:
      prop.validate(None, 3.5)
      prop.validate(None, 4)
    
    assert prop._from_storage(4.000001) == 4.000001
    
    assert prop.to_search_field() == search.NumberField
    assert prop.to_datastore_property() == ndb.FloatProperty
  
  def test_integer_property(self):
    prop = venom.Properties.Integer(min=2, max=8, choices=[1, 3, 4, 9], required=True)
    
    assert prop.min == 2
    assert prop.max == 8
    assert prop.choices == [1, 3, 4, 9]
    assert prop.required == True
    
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None, 1)
      prop.validate(None, 9)
    with smart_assert.raises() as context:
      prop.validate(None, 3)
      prop.validate(None, 4)
    
    assert prop._from_storage(4.000001) == 4
    
    assert prop.to_search_field() == search.NumberField
    assert prop.to_datastore_property() == ndb.IntegerProperty
  
  def test_choices_property(self):
    prop = venom.Properties.ChoicesProperty(choices=[1, 2, 3, '4'])
    
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None, 4)
      prop.validate(None, None)
    with smart_assert.raises() as context:
      prop.validate(None, 1)
      prop.validate(None, 2)
      prop.validate(None, 3)
      prop.validate(None, '4')
  
  def test_validate_on_set(self):
    class ModelStub(venom.Model):
      prop = venom.Properties.Property(required=True)
    
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      model = ModelStub()
      model.prop = None
    
    class ModelStub(venom.Model):
      prop = venom.Properties.Property(required=False)
    
    model = ModelStub()
    model.prop = None
  
  def test_invalid_comparison(self):
    prop = venom.Properties.Property()
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop == 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop < 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop <= 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop > 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop >= 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop != 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop.contains(1)
    
    class TestProp(venom.Properties.Property):
      allowed_operators = frozenset([
        venom.Properties.PropertyComparison.EQ,
        venom.Properties.PropertyComparison.NE
      ])
      
      def query_uses_datastore(self, operator, value):
        return operator == venom.Properties.PropertyComparison.EQ
      
      def to_search_field(self, operator, value):
        return 'search'
  
      def to_datastore_property(self, operator, value):
        return 'datastore'
    
    prop = TestProp()
    with smart_assert.raises() as context:
      prop == 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop < 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop <= 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop > 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop >= 1
    with smart_assert.raises() as context:
      prop != 1
    with smart_assert.raises(venom.Properties.InvalidPropertyComparison) as context:
      prop.contains(1)
  
  def test_base_validatation(self):
    class TestProp(venom.Properties.Property):
      pass
    
    prop = TestProp(required=True)
    with smart_assert.raises() as context:
      prop.validate(None, 123)
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None, None)
    
    prop = TestProp(required=False)
    with smart_assert.raises() as context:
      prop.validate(None, 123)
      prop.validate(None, None)
  
  def test_set_value_vs_stored_value(self):
    class TestProp(venom.Properties.Property):
      def _set_stored_value(self, entity, value):
        super(TestProp, self)._set_stored_value(entity, value // 2)
  
      def _get_stored_value(self, entity):
        return super(TestProp, self)._get_stored_value(entity) * 2
    
    class ModelStub(object):
      pass
    entity = ModelStub()
    
    prop = TestProp()
    prop._connect(entity=entity)
    prop._set_value(entity, 123)
    assert prop._get_value(entity) == 123
    assert prop._get_stored_value(entity) == 246
    prop._set_stored_value(entity, 468)
    assert prop._get_value(entity) == 234
    assert prop._get_stored_value(entity) == 468


class PropComparisonTestProp(venom.Properties.Property):
  allowed_operators = venom.Properties.PropertyComparison.allowed_operators
  
  def query_uses_datastore(self, operator, value):
    return operator == venom.Properties.PropertyComparison.EQ
  
  def to_search_field(self, operator, value):
    return search.TextField

  def to_datastore_property(self):
    return ndb.StringProperty


class PropertyComparisonTest(BasicTestCase):
  def test_search_query_without_query_parameter(self):
    prop = PropComparisonTestProp()
    prop._connect(name='prop')
    comparison = prop == 123
    assert comparison.to_search_query([]) == 'prop = 123'
    comparison = prop < 123
    assert comparison.to_search_query([]) == 'prop < 123'
    comparison = prop <= 123
    assert comparison.to_search_query([]) == 'prop <= 123'
    comparison = prop > 123
    assert comparison.to_search_query([]) == 'prop > 123'
    comparison = prop >= 123
    assert comparison.to_search_query([]) == 'prop >= 123'
    comparison = prop != 123
    assert comparison.to_search_query([]) == '(NOT prop = 123)'
    comparison = prop == 'bar = "foo"'
    assert comparison.to_search_query([]) == 'prop = "bar = \\"foo\\""'
  
  def test_search_query_with_query_parameter(self):
    prop = PropComparisonTestProp()
    prop._connect(name='prop')
    comparison = prop == venom.QueryParameter()
    assert comparison.to_search_query(['foo']) == 'prop = "foo"'
    assert comparison.to_search_query([123]) == 'prop = 123'
    comparison = prop == venom.QueryParameter('bar')
    assert comparison.to_search_query(['foo']) == 'prop = "foo"'
  
  def test_datastore_query_without_query_parameter(self):
    prop = PropComparisonTestProp()
    prop._connect(name='prop')
    comparison = prop == '123'
    assert str(comparison.to_datastore_query([])) == "FilterNode('prop', '=', '123')"
    comparison = prop < '123'
    assert str(comparison.to_datastore_query([])) == "FilterNode('prop', '<', '123')"
    comparison = prop <= '123'
    assert str(comparison.to_datastore_query([])) == "FilterNode('prop', '<=', '123')"
    comparison = prop > '123'
    assert str(comparison.to_datastore_query([])) == "FilterNode('prop', '>', '123')"
    comparison = prop >= '123'
    assert str(comparison.to_datastore_query([])) == "FilterNode('prop', '>=', '123')"
    comparison = prop != '123'
    assert str(comparison.to_datastore_query([])) == "OR(FilterNode('prop', '<', '123'), FilterNode('prop', '>', '123'))"
  
  def test_datastore_query_with_query_parameter(self):
    prop = PropComparisonTestProp()
    prop._connect(name='prop')
    comparison = prop == venom.QueryParameter()
    assert str(comparison.to_datastore_query(['foo'])) == "FilterNode('prop', '=', 'foo')"
    assert str(comparison.to_datastore_query(['bar'])) == "FilterNode('prop', '=', 'bar')"
    comparison = prop == venom.QueryParameter('bar')
    args = comparison.to_query_arguments().apply(bar='foo')
    assert str(comparison.to_datastore_query(args)) == "FilterNode('prop', '=', 'foo')"
  
  def test_uses_datastore(self):
    prop = PropComparisonTestProp()
    prop._connect(name='prop')
    comparison = prop == venom.QueryParameter()
    assert comparison.uses_datastore()
    comparison = prop < venom.QueryParameter()
    assert not comparison.uses_datastore()
