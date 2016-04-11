__all__  = ['Query', 'PropertyQuery', 'QueryDict']
__all__ += ['QueryOperator', 'AND', 'OR']


class QueryComponent(object):
  def get_properties(self):
    raise NotImplementedError()
  
  def uses_search_api(self):
    raise NotImplementedError()
  
  def to_query_string(self):
    raise NotImplementedError()
  
  def get_property_queries(self):
    raise NotImplementedError()
  
  @classmethod
  def require(cls, objects):
    for obj in objects:
      if not isinstance(obj, cls):
        raise Exception('{} found when expecting an instance of QueryComponent'.format(obj))


class PropertyQuery(QueryComponent):
  EQ = '='
  NE = '!='
  LT = '<'
  LE = '<='
  GT = '>'
  GE = '>='
  IN = 'in'

  def __init__(self, prop, operator, value):
    self.property = prop
    self.operator = operator
    self.value = value
  
  def __repr__(self):
    return self.to_query_string()
  
  def get_property_queries(self):
    return [self]
  
  def get_properties(self):
    return [self.property]
  
  def uses_search_api(self):
    return self.property.search
  
  def to_query_string(self):
    return '{} {} {!r}'.format(self.property._code_name, self.operator, self.value) 


class Query(QueryComponent):
  def __init__(self, *queries):
    QueryComponent.require(queries)
    self.queries = queries
    self._and = AND(*queries)
  
  def uses_search_api(self):
    return self._contains_search_property() or self._contains_illegal_query()
  
  def _contains_search_property(self):
    return self._and.uses_search_api()
  
  def _contains_illegal_query(self):
    return self._contains_multiple_inequalities()
  
  def _contains_multiple_inequalities(self):
    inequalities = set()
    for param_query in self._and.get_property_queries():
      if param_query.operator != PropertyQuery.EQ:
        inequalities.add(param_query.property)
        if len(inequalities) > 1:
          return True
    return False
  
  def get_property_queries(self):
    return self._and.get_property_queries()
  
  def get_properties(self):
    return self._and.get_properties()
  
  def to_query_string(self):
    return self._and.to_query_string()
          

class QueryDict(dict):
  def get_search_properties(self):
    properties = set()
    for _, query in self.items():
      if not isinstance(query, Query):
        continue
      if query.search:
        properties |= query.properties
    return properties
      

class QueryOperator(QueryComponent):
  def __init__(self, *queries):
    QueryComponent.require(queries)
    self.queries = queries
  
  def get_property_queries(self):
    properties = set()
    for query in self.queries:
      properties |= set(query.get_property_queries())
    return properties
  
  def get_properties(self):
    properties = set()
    for query in self.queries:
      properties |= set(query.get_properties())
    return properties
  
  def uses_search_api(self):
    for query in self.queries:
      if query.uses_search_api():
        return True
    return False


class AND(QueryOperator):
  def __repr__(self):
    return 'AND({})'.format(', '.join(map(repr, self.queries)))
  
  def to_query_string(self):
    query_strings = map(lambda x: x.to_query_string(), self.queries)
    query_string = ' AND '.join(query_strings)
    return '({})'.format(query_string)


class OR(QueryOperator):
  def __repr__(self):
    return 'OR({})'.format(', '.join(map(repr, self.queries)))
  
  def to_query_string(self):
    query_strings = map(lambda x: x.to_query_string(), self.queries)
    query_string = ' OR '.join(query_strings)
    return '({})'.format(query_string)
