from helper import smart_assert, BasicTestCase
import venom


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
      foo = venom.ModelAttribute()
      bar = venom.ModelAttribute()
    
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
    
  
  
  
