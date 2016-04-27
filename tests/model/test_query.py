from google.appengine.ext import ndb
from google.appengine.api import search
from helper import smart_assert, BasicTestCase
import venom


class QueryParameterTest(BasicTestCase):
  def test_args_only(self):
    param = venom.QueryParameter()
    args = ['foo', 'bar', 'baz']

    assert param.get_value(args) == 'foo'
    assert param.get_value(args) == 'bar'
    assert param.get_value(args) == 'baz'
    assert args == []
    
    with smart_assert.raises(IndexError) as context:
      param.get_value(args)


class PropComparisonTestProp(venom.Properties.Property):
  allowed_operators = venom.Properties.PropertyComparison.allowed_operators
  
  def query_uses_datastore(self, operator, value):
    return operator == venom.Properties.PropertyComparison.EQ
  
  def to_search_field(self, operator, value):
    return search.NumberField

  def to_datastore_property(self):
    return ndb.IntegerProperty


class QueryLogicalOperatorTest(BasicTestCase):
  def test_check_base_class_fails(self):
    foo = PropComparisonTestProp()
    foo._connect(name='foo')
    bar = PropComparisonTestProp()
    bar._connect(name='bar')
    
    operator = venom.QueryLogicalOperator(foo == 123, bar == 456)
    with smart_assert.raises(ValueError) as context:
      operator.to_search_query([])
  
  def test_get_property_comparisons(self):
    foo = PropComparisonTestProp()
    foo._connect(name='foo')
    bar = PropComparisonTestProp()
    bar._connect(name='bar')
    
    operator = venom.AND(foo == 1, bar == 2)
    assert len(operator.get_property_comparisons()) == 2
    
    operator = venom.AND(operator, bar > 2)
    assert len(operator.get_property_comparisons()) == 3
  
  def test_uses_datastore(self):
    foo = PropComparisonTestProp()
    foo._connect(name='foo')
    bar = PropComparisonTestProp()
    bar._connect(name='bar')
    
    operator = venom.AND(foo == 1, bar == 2)
    assert operator.uses_datastore()
    
    operator = venom.AND(operator, bar > 2)
    assert not operator.uses_datastore()
    
    operator = venom.OR(foo == 1, bar == 2)
    assert operator.uses_datastore()
    
    operator = venom.OR(operator, bar > 2)
    assert not operator.uses_datastore()
  
  def test_to_search_query(self):
    foo = PropComparisonTestProp()
    foo._connect(name='foo')
    bar = PropComparisonTestProp()
    bar._connect(name='bar')
    
    and_operator = venom.AND(foo > 1, bar != 18)
    assert and_operator.to_search_query([]) == '(foo > 1 AND (NOT bar = 18))'
    
    or_operator = venom.OR(foo > 1, bar != 18)
    assert or_operator.to_search_query([]) == '(foo > 1 OR (NOT bar = 18))'
    
    combined_operator = venom.AND(and_operator, or_operator)
    assert combined_operator.to_search_query([]) == '((foo > 1 AND (NOT bar = 18)) AND (foo > 1 OR (NOT bar = 18)))'
  
  def test_to_datastore_query(self):
    foo = PropComparisonTestProp()
    foo._connect(name='foo')
    bar = PropComparisonTestProp()
    bar._connect(name='bar')
    
    and_operator = venom.AND(foo > 1, bar != 18)
    assert str(and_operator.to_datastore_query([])) == "OR(AND(FilterNode('foo', '>', 1), FilterNode('bar', '<', 18)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '>', 18)))"
    
    or_operator = venom.OR(foo > 1, bar != 18)
    assert str(or_operator.to_datastore_query([])) == "OR(FilterNode('foo', '>', 1), FilterNode('bar', '<', 18), FilterNode('bar', '>', 18))"
    
    combined_operator = venom.AND(and_operator, or_operator)
    assert str(combined_operator.to_datastore_query([])) == "OR(AND(FilterNode('foo', '>', 1), FilterNode('bar', '<', 18), FilterNode('foo', '>', 1)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '<', 18), FilterNode('bar', '<', 18)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '<', 18), FilterNode('bar', '>', 18)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '>', 18), FilterNode('foo', '>', 1)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '>', 18), FilterNode('bar', '<', 18)), AND(FilterNode('foo', '>', 1), FilterNode('bar', '>', 18), FilterNode('bar', '>', 18)))"
    
    
class QueryTestProp(venom.Properties.Property):
  allowed_operators = venom.Properties.PropertyComparison.allowed_operators

  def query_uses_datastore(self, operator, value):
    return True

  def to_search_field(self, operator, value):
    return search.NumberField

  def to_datastore_property(self):
    return ndb.IntegerProperty
    

class QueryTest(BasicTestCase):
  def test_query_inheritance(self):
    foo = QueryTestProp()
    foo._connect(name='foo')
    bar = QueryTestProp()
    bar._connect(name='bar')
    
    query = venom.Query(foo == 123, bar == 456)
    query._connect(name='query')
    
    assert query.to_search_query([]) == '(foo = 123 AND bar = 456)'
    assert query._name == 'query'
    assert query._model == None
    assert query._entity == None
  
  def test_uses_datastore(self):
    foo = QueryTestProp()
    foo._connect(name='foo')
    bar = QueryTestProp()
    bar._connect(name='bar')
    
    query = venom.Query(foo == 123, bar == 456)
    query._connect(name='query')
    assert query.uses_datastore()
    
    query = venom.Query(foo == 123, bar != 456)
    query._connect(name='query')
    assert query.uses_datastore()
    
    query = venom.Query(foo > 123, bar != 456)
    query._connect(name='query')
    assert not query.uses_datastore()
    
    query = venom.Query(foo > 123, foo != 456)
    query._connect(name='query')
    assert query.uses_datastore()
    
  def test_callable(self):
    class TestModel(venom.Model):
      pass
    
    foo = QueryTestProp()
    foo._connect(name='foo')
    bar = QueryTestProp()
    bar._connect(name='bar')
    
    query = venom.Query(foo == venom.QP, bar == venom.QP)
    query._connect(name='query', entity=TestModel())
    assert query(123, 456) == []
    
    query = venom.Query(foo < venom.QP, bar != venom.QP)
    query._connect(name='query', entity=TestModel())
    assert query(123, bar=456) == []
    