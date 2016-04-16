# app engine imports
from google.appengine.ext import ndb

# package imports
from model import ModelAttribute
# Query._uses_illegal_query contains an import too


__all__ = [
  'QueryParameter', 'QueryComponent', 'QueryLogicalOperator',
  'AND', 'OR', 'QueryResults', 'Query'
]


class QueryParameter(object):
  def __init__(self, key=None):
    self.key = key
  
  def get_value(self, args, kwargs):
    if self.key == None:
      return self._get_value_from_args(args)
    return self._get_value_from_kwargs(kwargs)
  
  def _get_value_from_args(self, args):
    if len(args) == 0:
      raise IndexError('Not enough arguments for Query to execute')
    
    value = args[0]
    del args[0]
    return value
  
  def _get_value_from_kwargs(self, kwargs):
    if not self.key in kwargs:
      raise KeyError('Parameter keyword "{}" not found in {}'.format(self.key, kwargs))
    
    value = kwargs[self.key]
    del kwargs[self.key]
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
  
  def uses_datastore(self):
    raise NotImplementedError()
  
  def get_property_comparisons(self):
    raise NotImplementedError()
  
  def to_datastore_query(self, args, kwargs):
    raise NotImplementedError()
  
  def to_search_query(self, args, kwargs):
    raise NotImplementedError()


class QueryLogicalOperator(QueryComponent):
  datastore_conjuntion = None
  search_conjunction = None
  
  def __init__(self, *components):
    self.components = components
  
  """ [below] Implemented from QueryComponent """
  
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
  
  def to_datastore_query(self, args, kwargs):
    if self.datastore_conjuntion == None:
      raise ValueError('self.datastore_conjuntion cannot be None')
    return self.datastore_conjuntion(
      *map(lambda component: component.to_datastore_query(args, kwargs), self.components))
  
  def to_search_query(self, args, kwargs):
    if self.datastore_conjuntion == None:
      raise ValueError('self.search_conjunction cannot be None')
    query_strings = map(lambda component: component.to_search_query(args, kwargs), self.components)
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
  pass


class Query(AND, ModelAttribute):
  def __init__(self, *components):
    super(Query, self).__init__(*components)
  
  """ [below] Implemented from QueryComponent """
  
  def uses_datastore(self):
    return super(Query, self).uses_datastore() and not self._uses_illegal_query()
  
  """ [end] QueryComponent implementation """
  
  def _uses_illegal_query(self):
    # places here to avoid circular imports
    from Properties import PropertyComparison
    inequalities = set()
    for comparison in self.get_property_comparisons():
      if comparison.operator != PropertyComparison.EQ:
        inequalities.add(comparison.property)
        if len(inequalities) > 1:
          return True
    return False
  
  def __call__(self, *args, **kwargs):
    if self.uses_datastore():
      query = self.to_datastore_query(args, kwargs)
      results = self._entity._execute_datastore_query(query)
      return QueryResults(results)
    else:
      query = self.to_search_query(args, kwargs)
      results = self._entity._execute_search_query(query)
      return QueryResults(results)
