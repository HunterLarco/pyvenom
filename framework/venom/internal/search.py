# app engine imports
from google.appengine.api import search 


__all__ = ['SearchModel']
__all__ += ['SearchField', 'TextField', 'AtomField', 'NumberField', 'DateField', 'GeopointField']
__all__ += ['PopulateKeywordArgNotFound']
__all__ += ['SearchQuery', 'AND', 'OR']


class PopulateKeywordArgNotFound(Exception):
  pass


class SearchQuery(object):
  def __init__(self, tagname, operator, value):
    self.tagname = tagname
    self.operator = operator
    self.value = value
  
  def query_string(self):
    return '{}{}{}'.format(self.tagname, self.operator, self.value)
  
  def __repr__(self):
    return 'SearchQuery({})'.format(self.query_string())


class AND(object):
  def __init__(self, *queries):
    self.queries = queries
  
  def query_string(self):
    values = map(lambda x: x.query_string(), self.queries)
    return '({})'.format(' AND '.join(values))
  
  def __repr__(self):
    return 'AND({})'.format(', '.join(map(str, self.queries)))


class OR(object):
  def __init__(self, *queries):
    self.queries = queries
  
  def query_string(self):
    values = map(lambda x: x.query_string(), self.queries)
    return '({})'.format(' OR '.join(values))
  
  def __repr__(self):
    return 'OR({})'.format(', '.join(map(str, self.queries)))


class SearchField(object):
  name = None
  
  def convert(self, value):
    raise NotImplementedError('SearchField convert method not implemented')
  
  def deconvert(self, value):
    raise NotImplementedError('SearchField deconvert method not implemented')
  
  def __eq__(self, value):
    raise NotImplementedError()
  
  def __ne__(self, value):
    raise NotImplementedError()
  
  def __lt__(self, value):
    raise NotImplementedError()
  
  def __le__(self, value):
    raise NotImplementedError()
  
  def __gt__(self, value):
    raise NotImplementedError()
  
  def __ge__(self, value):
    raise NotImplementedError()
  
  def __repr__(self):
    return '{}(name={})'.format(self.__class__.__name__, self.name)


class TextField(SearchField):
  def convert(self, value):
    return search.TextField(name=self.name, value=str(value))
  
  def deconvert(self, value):
    return value
  
  def __eq__(self, value):
    return SearchQuery(self.name, '=', value)


class AtomField(SearchField):
  def convert(self, value):
    return search.TextField(name=self.name, value=str(value))
  
  def deconvert(self, value):
    return value
  
  def __eq__(self, value):
    return SearchQuery(self.name, '=', value)


class NumberField(SearchField):
  def convert(self, value):
    return search.TextField(name=self.name, value=float(value))
  
  def deconvert(self, value):
    return value
  
  def __eq__(self, value):
    return SearchQuery(self.name, '=', value)
  
  def __lt__(self, value):
    return SearchQuery(self.name, '<', value)
  
  def __le__(self, value):
    return SearchQuery(self.name, '<=', value)
  
  def __gt__(self, value):
    return SearchQuery(self.name, '>', value)
  
  def __ge__(self, value):
    return SearchQuery(self.name, '>=', value)


class DateField(SearchField):
  def convert(self, value):
    return search.DateField(name=self.name, value=value)
  
  def deconvert(self, value):
    return value
  
  def __eq__(self, value):
    return SearchQuery(self.name, '=', value)
  
  def __lt__(self, value):
    return SearchQuery(self.name, '<', value)
  
  def __le__(self, value):
    return SearchQuery(self.name, '<=', value)
  
  def __gt__(self, value):
    return SearchQuery(self.name, '>', value)
  
  def __ge__(self, value):
    return SearchQuery(self.name, '>=', value)


class GeopointField(SearchField):
  def convert(self, value):
    lat, lon = value
    geopt = search.GeoPoint(lat, lon)
    return search.GeoField(name=self.name, value=geopt)
  
  def deconvert(self, geopt):
    return (geopt.latitude, geopt.longitude)
  
  def __call__(self, lat, lon):
    return GeopointDistance(self, lat, lon)


class GeopointDistance(object):
  def __init__(self, geofield, lat, lon):
    self.geofield = geofield
    self.lat = lat
    self.lon = lon
    self.name = 'distance({}, geopoint({}, {}))'.format(self.geofield.name, self.lat, self.lon)
  
  def __lt__(self, value):
    return SearchQuery(self.name, '<', value)
  
  def __gt__(self, value):
    return SearchQuery(self.name, '>', value)


class MetaSearchModel(type):
  def __init__(cls, name, bases, classdict):
    super(MetaSearchModel, cls).__init__(name, bases, classdict)
    cls._build_index()
    cls._name_properties()


class SearchModel(object):
  __metaclass__ = MetaSearchModel
  
  _prefix = 'VenomIndex'
  
  def __init__(self, **kwargs):
    self.id = None
    self._clear_parameters()
    self.populate(**kwargs)
  
  @classmethod
  def _build_index(cls):
    cls._index_name = '{}.{}'.format(cls._prefix, cls.__name__)
    cls._index = search.Index(name=cls._index_name)
  
  @classmethod
  def _name_properties(cls):
    cls._parameters = {}
    props = dir(cls)
    for prop in props:
      value = getattr(cls, prop)
      if isinstance(value, SearchField):
        value.name = prop
        cls._parameters[prop] = value
    cls._parameters
  
  def _clear_parameters(self):
    for key, value in self._parameters.items():
      setattr(self, key, None)
  
  def populate(self, **kwargs):
    for key, value in kwargs.items():
      if not key in self._parameters:
        raise PopulateKeywordArgNotFound()
      setattr(self, key, value)
  
  def _to_document(self):
    fields = []
    for key, modelfield in self._parameters.items():
      value = getattr(self, key)
      fields.append(modelfield.convert(value))
    return search.Document(fields=fields)
  
  def put(self):
    results = self._index.put(self._to_document())
    result = results[0]
    identifier = result.id
    self.id = identifier
  
  @classmethod
  def _document_to_model(cls, document):
    model = cls()
    kwargs = {}
    fields = document.fields
    for field in fields:
      name = field.name
      value = field.value
      if name in cls._parameters:
        kwargs[name] = getattr(cls, name).deconvert(value)
    model.populate(**kwargs)
    model.id = document.doc_id
    return model
  
  @classmethod
  def get(cls, identifier):
    return cls._index.get(identifier)
  
  @classmethod
  def query(cls, *query_params):
    query_string = AND(*query_params).query_string()
    results = cls._index.search(query_string)
    return map(cls._document_to_model, results.results)
  
  def __repr__(self):
    params = ['{}={!r}'.format(key, getattr(self, key)) for key, value in self._parameters.items()]
    params.append('id={!r}'.format(self.id))
    return '{}({})'.format(self.__class__.__name__, ', '.join(params))
  
  
