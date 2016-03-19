__all__ = []


from google.appengine.ext import ndb


# TODO: indexed restrictions
PropertyChoices = {
  ndb.StringProperty   : 'String',
  ndb.IntegerProperty  : 'Integer',
  ndb.FloatProperty    : 'Float',
  ndb.BooleanProperty  : 'Boolean',
  ndb.TextProperty     : 'Text',
  ndb.KeyProperty      : 'Key',
  ndb.DateTimeProperty : 'DateTime',
  ndb.BlobProperty     : 'Blob'
}


class _VenomScaffoldModelProperty(ndb.Model):
  type = ndb.StringProperty(indexed=False, choices=PropertyChoices.values())
  name = ndb.StringProperty(indexed=False)
  documentation = ndb.TextProperty(indexed=False)


class _VenomScaffoldModelMethod(ndb.Model):
  name = ndb.StringProperty(indexed=False)
  args = ndb.StringProperty(indexed=False, repeated=True)
  kwargs = ndb.PickleProperty(indexed=False, repeated=True)
  body = ndb.TextProperty(indexed=False)
  documentation = ndb.TextProperty(indexed=False)


class _VenomScaffoldModel(ndb.Model):
  name = ndb.StringProperty(indexed=True)
  properties = ndb.LocalStructuredProperty(_VenomScaffoldModelProperty, repeated=True, indexed=False)
  methods = ndb.LocalStructuredProperty(_VenomScaffoldModelMethod, repeated=True, indexed=False)


def convertModelToScaffold(model):
  props = []
  methods = []
  
  attributes = set(dir(model)) - set(dir(ndb.Model))
  for attribute in attributes:
    value = getattr(model, attribute)
    if isinstance(value, ndb.Property):
      
      prop = _VenomScaffoldModelProperty()
      prop.name = attribute
      prop.documentation = ''
      prop.type = PropertyChoices[value.__class__]
      props.append(prop)
    
    elif hasattr(value, '__call__'):
    
      import inspect
      method = _VenomScaffoldModelMethod()
      method.name = attribute
      method.documentation = value.__doc__
      method.body = inspect.getsourcelines(value)
      method.args = []
      method.kwargs = []
      methods.append(method)
  
  scaffold = _VenomScaffoldModel()
  scaffold.name = model.__name__
  scaffold.properties = props
  scaffold.methods = methods
  
  scaffold.put()
  return scaffold
  