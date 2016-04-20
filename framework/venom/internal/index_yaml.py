__all__ = ['IndexYaml']


class IndexYaml(object):
  def __init__(self, schemas=None):
    self.schemas = schemas if schemas else []
  
  def _schema_to_yaml(self, schema):
    yaml  = '- kind: {}'.format(schema._model.kind) + '\n'
    yaml += '  properties:' + '\n'
    properties = []
    for name, prop_schema in schema.items():
      if prop_schema.datastore and prop_schema.indexed_datastore:
        properties.append('  - name: {}'.format(name))
    properties.sort()
    if len(properties) == 0:
      return None
    return yaml + '\n'.join(properties)
  
  def add_schema(self, schema):
    self.schemas.append(schema)
  
  def generate(self):
    yaml = 'indexes:'
    
    schema_yamls = []
    for schema in self.schemas:
      schema_yaml = self._schema_to_yaml(schema)
      if schema_yaml:
        schema_yamls.append(schema_yaml)
    
    return yaml + '\n\n' + '\n\n'.join(schema_yamls)
