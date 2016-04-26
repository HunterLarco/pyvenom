# system imports
import inspect

# app engine imports
from google.appengine.ext import ndb

# package imports
from attribute import ModelAttribute


__all__ = [
  'QueryParameter', 'QP', 'QueryComponent', 'QueryLogicalOperator',
  'AND', 'OR', 'QueryResults', 'Query', 'PropertyComparison',
  'QueryArgument', 'QueryArgumentList'
]


class QueryArgument(object):
  def __init__(self, key, optional_key=True):
    self.key = key
    self.optional_key = optional_key
  
  def __repr__(self):
    return 'QueryArgument({!r}, optional_key={!s})'.format(self.key, self.optional_key)


class QueryArgumentList(list):
  def apply(self, *args, **kwargs):
    singleton = lambda: None
    result_args = [singleton] * len(self)
    
    query_kwarg_keys = { query_arg.key for query_arg in self }
    
    for key in kwargs:
      if not key in query_kwarg_keys:
        raise Exception('Unknown key {}'.format(key))
    
    if len(kwargs) + len(args) != len(self):
      raise Exception('Expected {} args, received {}'.format(len(self), len(kwargs) + len(args)))
    
    for i, query_arg in enumerate(self):
      if query_arg.key in kwargs:
        result_args[i] = kwargs[query_arg.key]
      elif not query_arg.optional_key:
        raise Exception('Key not found when required {}'.format(query_arg.key))
    
    j = 0
    for i, result_arg in enumerate(result_args):
      if result_arg == singleton:
        result_args[i] = args[j]
        j += 1
    
    return result_args
  
  def __repr__(self):
    return 'QueryArgumentList({})'.format(super(QueryArgumentList, self).__repr__())


class QueryParameter(object):
  default_singleton = lambda: None
  
  def __init__(self, key=None, default=default_singleton):
    self.key = key
    self.default = default
  
  def has_default(self):
    return self.default != self.default_singleton
  
  def get_value(self, args):
    if len(args) == 0:
      raise IndexError('Not enough arguments for Query to execute')
    
    value = args[0]
    del args[0]
    return value
  
QP = QueryParameter


class QueryComponent(object):
  """
  ' Used to provide common functionality across all query
  ' components. This is why querys can be formed by many
  ' different combinations of QueryComponents: they all
  ' provide the same data just in different ways through
  ' these methods.
  """
  
  def to_query_arguments(self):
    raise NotImplementedError()
  
  def uses_datastore(self):
    raise NotImplementedError()
  
  def get_property_comparisons(self):
    raise NotImplementedError()
  
  def to_datastore_query(self, args):
    raise NotImplementedError()
  
  def to_search_query(self, args):
    raise NotImplementedError()


class PropertyComparison(QueryComponent):
  EQ = '='
  NE = '!='
  LT = '<'
  LE = '<='
  GT = '>'
  GE = '>='
  IN = 'in'
  
  allowed_operators = frozenset((EQ, NE, LT, LE, GT, GE, IN))
  
  def __init__(self, property, operator, value):
    if not operator in self.allowed_operators:
      raise Exception('Unknown operator "{}"'.format(operator))
    
    self.property = property
    self.operator = operator
    self.value = value
  
  """ [below] Implemented from QueryComponent """
  
  def to_query_arguments(self):
    if isinstance(self.value, QueryParameter):
      if self.value.key:
        return QueryArgumentList([ QueryArgument(self.value.key, optional_key=False) ])
      return QueryArgumentList([ QueryArgument(self.property._name, optional_key=True) ])
    elif inspect.isclass(self.value) and issubclass(self.value, QueryParameter):
      return QueryArgumentList([ QueryArgument(self.property._name, optional_key=True) ])
    return QueryArgumentList()
  
  def uses_datastore(self):
    return self.property.query_uses_datastore(self.operator, self.value)
  
  def get_property_comparisons(self):
    return [self]
  
  def to_datastore_query(self, args):
    prop = self.property.to_datastore_property()
    if inspect.isclass(prop):
      prop = prop(indexed=True, name=self.property._name)
    else:
      prop._name = self.property._name
      prop._indexed = True
    value = self.value
    if isinstance(self.value, QueryParameter):
      value = self.value.get_value(args)
    elif inspect.isclass(self.value) and issubclass(self.value, QueryParameter):
      value = self.value().get_value(args)
    value = self.property._to_storage(value)
    if   self.operator == self.EQ: return prop == value
    elif self.operator == self.NE: return prop != value
    elif self.operator == self.LT: return prop < value
    elif self.operator == self.LE: return prop <= value
    elif self.operator == self.GT: return prop > value
    elif self.operator == self.GE: return prop >= value
    elif self.operator == self.IN: return prop.IN(value)
    else: raise Exception('Unknown operator')
  
  def to_search_query(self, args):
    value = self.value
    if isinstance(self.value, QueryParameter):
      value = self.value.get_value(args)
    elif inspect.isclass(self.value) and issubclass(self.value, QueryParameter):
      value = self.value().get_value(args)
    value = self.property._to_storage(value)
    if isinstance(value, str):
      value = '"{}"'.format(value.replace('"', '\\"'))
    if self.operator == self.NE:
      return '(NOT {} = {})'.format(self.property._name, value)
    return '{} {} {}'.format(self.property._name, self.operator, value)
  
  """ [end] QueryComponent implementation """


class QueryLogicalOperator(QueryComponent):
  datastore_conjuntion = None
  search_conjunction = None
  
  def __init__(self, *components):
    self.components = components
  
  """ [below] Implemented from QueryComponent """
  
  def to_query_arguments(self):
    arguments = QueryArgumentList()
    for component in self.components:
      arguments.extend(component.to_query_arguments())
    return arguments
  
  def uses_datastore(self):
    """ If a single component uses the search api
        so must this function """
    for component in self.components:
      if not component.uses_datastore():
        return False
    return True
  
  def get_property_comparisons(self):
    property_comparisons = []
    for component in self.components:
      property_comparisons.extend(component.get_property_comparisons())
    return property_comparisons
  
  def to_datastore_query(self, args):
    if self.datastore_conjuntion == None:
      raise ValueError('self.datastore_conjuntion cannot be None')
    if not self.components:
      return None
    return self.datastore_conjuntion(
      *map(lambda component: component.to_datastore_query(args), self.components))
  
  def to_search_query(self, args):
    if self.datastore_conjuntion == None:
      raise ValueError('self.search_conjunction cannot be None')
    query_strings = map(lambda component: component.to_search_query(args), self.components)
    query_string = ' {} '.format(self.search_conjunction).join(query_strings)
    return '({})'.format(query_string)
  
  """ [end] QueryComponent implementation """


class AND(QueryLogicalOperator):
  datastore_conjuntion = ndb.AND
  search_conjunction = 'AND'


class OR(QueryLogicalOperator):
  datastore_conjuntion = ndb.OR
  search_conjunction = 'OR'


class QueryResults(list):
  def get(self):
    return self[0] if len(self) > 0 else None
  
  def count(self):
    return len(self)
  
  def fetch(self, count, offset=0):
    return self[offset: offset + count]


class Query(AND, ModelAttribute):
  def __init__(self, *components):
    super(Query, self).__init__(*components)
  
  """ [below] Implemented from QueryComponent """
  
  def uses_datastore(self):
    return super(Query, self).uses_datastore() and not self._uses_illegal_query()
  
  """ [end] QueryComponent implementation """
  
  def _uses_illegal_query(self):
    inequalities = set()
    for comparison in self.get_property_comparisons():
      if comparison.operator != PropertyComparison.EQ:
        inequalities.add(comparison.property)
        if len(inequalities) > 1:
          return True
    return False
  
  def __call__(self, *args, **kwargs):
    query_arguments = self.to_query_arguments()
    arguments = query_arguments.apply(*args, **kwargs)
    
    if self.uses_datastore():
      query = self.to_datastore_query(arguments)
      results = self._model._execute_datastore_query(query)
      return QueryResults(results)
    else:
      query = self.to_search_query(arguments)
      results = self._model._execute_search_query(query)
      return QueryResults(results)
