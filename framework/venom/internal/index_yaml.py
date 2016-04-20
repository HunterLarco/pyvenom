# vendor imports
import yaml as pyyaml


__all__ = ['IndexYaml', 'IndexGenerator']


class IndexYaml(dict):
  def __init__(self, yaml):
    yaml = pyyaml.load(yaml)
    if not yaml:
      yaml = { 'indexes': [] }
    super(IndexYaml, self).__init__(yaml)
    self.validate()
  
  def __str__(self):
    dumped_models = self._dump_models()
    yaml = 'indexes:\n\n{}'.format(dumped_models)
    return yaml
  
  def _dump_models(self):
    models = self['indexes']
    dumps = []
    for model in models:
      dumps.append(self._dump_model(model))
    return '\n\n'.join(dumps)
  
  def _dump_model(self, model):
    kind = model['kind']
    properties = model['properties']
    yaml = '- kind: {}\n'.format(kind)
    if 'ancestor' in model:
      ancestor = model['ancestor']
      ancestor_str = 'yes' if ancestor else 'no'
      yaml += '  ancestor: {}\n'.format(ancestor_str)
    yaml += '  properties:\n'
    yaml += self._dump_properties(properties)
    return yaml
  
  def _dump_properties(self, properties):
    dumps = []
    for prop in properties:
      dumps.append(self._dump_property(prop))
    return '\n'.join(dumps)
  
  def _dump_property(self, prop):
    name = prop['name']
    yaml = '  - name: {}'.format(name)
    if 'direction' in prop:
      direction = prop['direction']
      yaml += '\n    direction: {}'.format(direction)
    return yaml
  
  def validate(self):
    self._validate_root()
    self._validate_models()
  
  def _validate_root(self):
    if not isinstance(self, dict):
      raise Exception('Invalid Index YAML: root must be a dict')
    if not 'indexes' in self:
      raise Exception('Invalid Index YAML: Expected "indexes" in root')
    indexes = self['indexes']
    if not isinstance(indexes, list):
      raise Exception('Invalid Index YAML: "indexes" variable must be a list')
  
  def _validate_models(self):
    models = self['indexes']
    for model in models:
      self._validate_model(model)
  
  def _validate_model(self, model):
    if not isinstance(model, dict):
      raise Exception('Invalid Index YAML: model must be a dict')
    if not 'kind' in model:
      raise Exception('Invalid Index YAML: Expected "kind" in model')
    if not isinstance(model['kind'], str):
      raise Exception('Invalid Index YAML: "kind" variable must be a string')
    if not 'properties' in model:
      raise Exception('Invalid Index YAML: Expected "properties" in model')
    if not isinstance(model['properties'], list):
      raise Exception('Invalid Index YAML: "kind" variable must be a list')
    if 'ancestor' in model:
      if not isinstance(model['ancestor'], bool):
        raise Exception('Invalid Index YAML: "ancestor" variable must be a bool')
    self._validate_properties(model['properties'])
  
  def _validate_properties(self, properties):
    for prop in properties:
      self._validate_property(prop)
  
  def _validate_property(self, prop):
    if not isinstance(prop, dict):
      raise Exception('Invalid Index YAML: property must be a dict')
    if not 'name' in prop:
      raise Exception('Invalid Index YAML: Expected "name" in property')
    if not isinstance(prop['name'], str):
      raise Exception('Invalid Index YAML: "name" variable must be a string')
    if 'direction' in prop:
      if not isinstance(prop['direction'], str):
        raise Exception('Invalid Index YAML: "direction" variable must be a string')
      if not prop['direction'] in {'asc', 'desc'}:
        raise Exception('Invalid Index YAML: "direction" variable must be "asc" or "desc"')


class IndexGenerator(IndexYaml):
  def __init__(self, yaml=None, schemas=None):
    super(IndexGenerator, self).__init__(yaml)
    self.index = {
      model['kind']: model
      for model in self['indexes']
    }
    for schema in schemas:
      self.add_schema(schema)
  
  def add_schema(self, schema):
    kind = schema._model.kind
    if kind in self.index:
      self._update_schema(schema)
      return
    self._insert_schema(schema)

  def _update_schema(self, schema):
    kind = schema._model.kind
    model = self.index[kind]
    if 'ancestor' in model:
      del model['ancestor']
    model['properties'] = [
      { 'name': name }
      for name, prop_schema in schema.items()
      if prop_schema.datastore and prop_schema.indexed_datastore
    ]
  
  def _insert_schema(self, schema):
    kind = schema._model.kind
    model = {
      'kind': kind,
      'properties': [
        { 'name': name }
        for name, prop_schema in schema.items()
        if prop_schema.datastore and prop_schema.indexed_datastore
      ]
    }
    self['indexes'].append(model)
    self.index[kind] = model
