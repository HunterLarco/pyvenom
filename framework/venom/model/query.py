__all__ = [
  'QueryParameter', 'QueryComponent', 'QueryLogicalOperator',
  'AND', 'OR', 'QueryResults', 'Query'
]


class QueryParameter(object):
  def __init__(self, name=None):
    self.name = name
  
  def get_value(self, args, kwargs):
    if self.name == None:
      return self._get_value_from_args(args)
    return self._get_value_from_kwargs(kwargs)
  
  def _get_value_from_args(self, args):
    if len(args) == 0:
      raise Exception('Not enough arguments for Query to execute')
    
    value = args[0]
    del args[0]
    return value
  
  def _get_value_from_kwargs(self, kwargs):
    if not self.name in kwargs:
      raise Exception('Parameter keyword "{}" not found'.format(self.name))
    
    value = kwargs[self.name]
    del kwargs[self.name]
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
  
  def to_search_api_query(self, args, kwargs):
    raise NotImplementedError()


class QueryLogicalOperator(QueryComponent):
  pass


class AND(QueryLogicalOperator):
  pass


class OR(QueryLogicalOperator):
  pass


class QueryResults(list):
  pass


class Query(QueryComponent):
  pass
