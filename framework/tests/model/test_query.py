from helper import smart_assert, BasicTestCase
import venom


class QueryParameterTest(BasicTestCase):
  def test_args_only(self):
    param = venom.QueryParameter()
    args = ['foo', 'bar', 'baz']

    assert param.get_value(args, {}) == 'foo'
    assert param.get_value(args, {}) == 'bar'
    assert param.get_value(args, {}) == 'baz'
    assert args == []
    
    with smart_assert.raises(IndexError) as context:
      param.get_value(args, {})
  
  def test_kwargs_only(self):
    param = venom.QueryParameter('foo')
    kwargs = {
      'foo': 'bar',
      'bar': 'baz'
    }

    assert param.get_value([], kwargs) == 'bar'
    assert kwargs == { 'bar': 'baz' }
    
    with smart_assert.raises(KeyError) as context:
      param.get_value([], kwargs)
  