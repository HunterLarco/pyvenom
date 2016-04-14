from helper import smart_assert, BasicTestCase
import venom


class BasePropertyTest(BasicTestCase):
  def test_required_attribute(self):
    # required property cannot except None as its value
    with smart_assert.raises(venom.Properties.PropertyEnforcementFailed) as context:
      prop = venom.Properties.Property(required=True)
      prop.enforce(None)

    # non-required property must accept None without an error
    prop = venom.Properties.Property(required=False)
    prop.enforce(None)
  
  def test_choices_attribute(self):
    # enforcing a value not in choices throws an error
    prop = venom.Properties.Property(choices=[1, 2, 3])
    with smart_assert.raises(venom.Properties.PropertyEnforcementFailed) as context:
      prop.enforce(4)
    
    # 1 is in "choices" so no error is thrown
    prop.enforce(1)
  
  def test_hidden_attribute(self):
    prop = venom.Properties.Property(hidden=True)
    smart_assert(prop.hidden).true(
      '[fail] prop.hidden == True on Property(hidden=True)'
    )
    
    prop = venom.Properties.Property(hidden=False)
    smart_assert(prop.hidden).false(
      '[fail] prop.hidden == False on Property(hidden=False)'
    )
  
  def test_default_argument(self):
    default = 'this is a default string'
    prop = venom.Properties.Property(default=default)
    smart_assert(prop.__get__(123, None), default).equals(
      '[fail] prop default returned from __get__'
    )
  
  
  
