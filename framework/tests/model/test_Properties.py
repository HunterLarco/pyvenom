from helper import smart_assert, BasicTestCase
import venom


class BasePropertyTest(BasicTestCase):
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
      prop.IN(1)
    
    class TestProp(venom.Properties.Property):
      allowed_operators = frozenset([venom.Properties.PropertyComparison.EQ])
    
    prop = TestProp()
    with smart_assert.raises() as context:
      prop == 1
  
  def test_on_compare_method(self):
    class TestProp(venom.Properties.Property):
      allowed_operators = venom.Properties.PropertyComparison.allowed_operators
      
      def _on_compare(self, operator):
        if operator == venom.Properties.PropertyComparison.EQ:
          self.datastore = True
        else:
          self.search = True
    
    prop = TestProp()
    with smart_assert.raises() as context:
      prop == 1
    
    assert prop.search == False
    assert prop.datastore == True
    assert prop.compared == True
    
    prop < 4
    
    assert prop.search == True
    assert prop.datastore == True
    assert prop.compared == True
  
  def test_enforces_list(self):
    class TestProp(venom.Properties.Property):
      allowed_operators = venom.Properties.PropertyComparison.allowed_operators
      
      def to_search_fields(self):
        return 123
      
      def to_datastore_properties(self):
        return 456
    
    prop = TestProp()
    smart_assert(prop._to_search_fields()).type(list,
      message='prop._to_search_fields() must return a list')
    smart_assert(prop._to_datastore_properties()).type(list,
      message='prop._to_datastore_properties() must return a list')
    
    class TestProp2(venom.Properties.Property):
      allowed_operators = venom.Properties.PropertyComparison.allowed_operators
      
      def to_search_fields(self):
        return [123]
      
      def to_datastore_properties(self):
        return [456]
    
    prop = TestProp2()
    smart_assert(prop._to_search_fields()).type(list,
      message='prop._to_search_fields() must return a list')
    smart_assert(prop._to_datastore_properties()).type(list,
      message='prop._to_datastore_properties() must return a list')
  
  def test_base_validatation(self):
    class TestProp(venom.Properties.Property):
      pass
    
    prop = TestProp(required=True)
    with smart_assert.raises() as context:
      prop.validate(123)
    with smart_assert.raises(venom.Properties.PropertyValidationFailed) as context:
      prop.validate(None)
    
    prop = TestProp(required=False)
    with smart_assert.raises() as context:
      prop.validate(123)
      prop.validate(None)
  
  def test_set_value_vs_stored_value(self):
    class TestProp(venom.Properties.Property):
      def _set_stored_value(self, entity, value):
        super(TestProp, self)._set_stored_value(entity, value // 2)
  
      def _get_stored_value(self, entity):
        return super(TestProp, self)._get_stored_value(entity) * 2
    
    entity = {}
    prop = TestProp()
    prop._set_value(entity, 123)
    assert prop._get_value(entity) == 123
    assert prop._get_stored_value(entity) == 246
    prop._set_stored_value(entity, 468)
    assert prop._get_value(entity) == 234
    assert prop._get_stored_value(entity) == 468
