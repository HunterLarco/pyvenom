# system imports
import os

# vendor imports
import yaml as pyyaml

# package imports
from builtin_file import bfile


__all__  = ['IndexYaml', 'IndexYamlFromFile', 'IndexGenerator']
__all__ += ['update_index_yaml']


def update_index_yaml(models):
  is_dev = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
  if not is_dev:
    return False
  
  index = ''
  if os.path.isfile('index.yaml'):
    with open('index.yaml', 'r') as f:
      index = f.read()
  
  schemas = map(lambda model: model._schema, models)
  generator = IndexGenerator(yaml=index, schemas=schemas)
  generated = generator.generate()
  
  if generated.strip() == index.strip():
    return False
  
  with bfile('index.yaml', 'w+') as f:
    f.write(generated)
  
  return True


class IndexYaml(object):
  def __init__(self, yaml):
    yaml = pyyaml.load(yaml if yaml else '')
    if not yaml:
      yaml = { 'indexes': [] }
    elif not 'indexes' in yaml or not yaml['indexes']:
      yaml['indexes'] = []
    super(IndexYaml, self).__init__()
    self.yaml = yaml
    self.validate()
  
  def __iter__(self):
    return iter(self.yaml)
  
  def __getitem__(self, key):
    return self.yaml[key]
  
  def __delitem__(self, key):
    del self.yaml[key]
  
  def __setitem__(self, key, value):
    self.yaml[key] = value
  
  def __str__(self):
    cleaned_yaml = self._clean_yaml(self.yaml)
    if not cleaned_yaml:
      return ''
    sorted_yaml = self._sort_yaml(cleaned_yaml)
    yaml = pyyaml.safe_dump(sorted_yaml, allow_unicode=True, default_flow_style=False)
    yaml = yaml.replace('- kind:', '\n- kind:').strip()
    return yaml
  
  def _clean_yaml(self, yaml):
    return [
      model
      for model in yaml['indexes']
      if model['properties']
    ]
  
  def _sort_yaml(self, cleaned_yaml):
    models = cleaned_yaml[:]
    for model in models:
      model['properties'] = sorted(model['properties'], key=lambda prop: prop['name'])
    return sorted(models, key=lambda model: model['kind'])
  
  def validate(self):
    self._validate_root()
    self._validate_models()
  
  def _validate_root(self):
    if not isinstance(self.yaml, dict):
      raise Exception('Invalid Index YAML: root must be a dict')
    if not 'indexes' in self.yaml:
      raise Exception('Invalid Index YAML: Expected "indexes" in root')
    indexes = self.yaml['indexes']
    if not isinstance(indexes, list):
      raise Exception('Invalid Index YAML: "indexes" variable must be a list')
  
  def _validate_models(self):
    models = self.yaml['indexes']
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
      raise Exception('Invalid Index YAML: "properties" variable must be a list')
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


class IndexYamlFromFile(IndexYaml):
  venom_marker = '# VENOM INDEXES\n'
  venom_info = """\n# This index.yaml is automatically updated whenever the venom framework
# detects a schema change. If you want to manage the index.yaml file
# manually, remove the above marker line (the line saying "# VENOM INDEXES").
# If you want to manage some indexes manually, move them above the marker line.
# The index.yaml file is automatically uploaded to the admin console when
# you next deploy your application using appcfg.py.\n"""
  datastore_marker = '# AUTOGENERATED\n'
  
  def __init__(self, yaml):
    manual, venom, automatic = self._slice_yaml(yaml)
    self.automatic = automatic.strip()
    self.manual = manual.strip()
    if not self.manual:
      self.manual = 'indexes:'
    venom = 'indexes:\n' + venom if venom else None
    super(IndexYamlFromFile, self).__init__(venom)
  
  def _slice_yaml(self, yaml):
    venom_marker_index = yaml.find(self.venom_marker)
    datastore_marker_index = yaml.find(self.datastore_marker)
    
    if venom_marker_index == -1 and datastore_marker_index == -1:
      return yaml, '', ''
    elif venom_marker_index > -1 and datastore_marker_index == -1:
      datastore_marker_index = len(yaml)
    elif venom_marker_index == -1 and datastore_marker_index > -1:
      venom_marker_index = datastore_marker_index
    elif venom_marker_index > -1 and datastore_marker_index > -1:
      if venom_marker_index > datastore_marker_index:
        return self._slice_yaml(yaml[:venom_marker_index])
    
    manual = yaml[:venom_marker_index]
    venom = yaml[venom_marker_index + len(self.venom_marker): datastore_marker_index]
    automatic = yaml[datastore_marker_index + len(self.datastore_marker):]
    return manual, venom, automatic
  
  def __str__(self):
    string = '{}\n\n{}{}\n{}'.format(
      self.manual,
      self.venom_marker, self.venom_info, super(IndexYamlFromFile, self).__str__())
    string += '\n\n{}\n{}'.format(self.datastore_marker, self.automatic)
    return string
    
    
class IndexGenerator(object):
  yaml_parser = IndexYamlFromFile
  
  def __init__(self, yaml=None, schemas=None):
    super(IndexGenerator, self).__init__()
    self.yaml = self.yaml_parser(yaml)
    self.index = {
      model['kind']: model
      for model in self.yaml['indexes']
    }
    for schema in schemas:
      self.add_schema(schema)
  
  def add_schema(self, schema):
    kind = schema._model.kind
    if kind in self.index:
      self._update_schema(schema)
      return
    self._insert_schema(schema)

  def _get_properties_from_schema(self, schema):
    return [
      { 'name': name }
      for name, prop_schema in schema.items()
      if prop_schema.datastore and prop_schema.indexed_datastore
    ]

  def _update_schema(self, schema):
    kind = schema._model.kind
    model = self.index[kind]
    if 'ancestor' in model:
      del model['ancestor']
    model['properties'] = self._get_properties_from_schema(schema)
  
  def _insert_schema(self, schema):
    kind = schema._model.kind
    model = {
      'kind': kind,
      'properties': self._get_properties_from_schema(schema)
    }
    self.yaml['indexes'].append(model)
    self.index[kind] = model
  
  def generate(self):
    return str(self.yaml)
