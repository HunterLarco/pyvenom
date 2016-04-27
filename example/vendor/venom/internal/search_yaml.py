# system imports
import os

# package imports
from builtin_file import bfile
from index_yaml import IndexYaml, IndexYamlFromFile, IndexGenerator


__all__  = ['VenomIndexGenerator', 'VenomYamlFromFile']
__all__ += ['update_search_yaml', 'load_search_schema', 'read_search_yaml']


def read_search_yaml():
  index = ''
  if os.path.isfile('search.venom.yaml'):
    with open('search.venom.yaml', 'r') as f:
      index = f.read()
  return index


def load_search_schema():
  return VenomYamlFromFile(read_search_yaml())


def update_search_yaml(models):
  is_dev = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
  if not is_dev:
    return False
  
  index = read_search_yaml()
  
  schemas = map(lambda model: model._schema, models)
  generator = VenomIndexGenerator(yaml=index, schemas=schemas)
  generated = generator.generate()
  
  if generated.strip() == index.strip():
    return False
  
  with bfile('search.venom.yaml', 'w+') as f:
    f.write(generated)
  
  return True


class VenomYamlFromFile(IndexYamlFromFile):
  venom_info = """\n# This search.yaml is automatically updated whenever the venom framework
# detects a schema change. If you want to manage the search.yaml file
# manually, remove the above marker line (the line saying "# VENOM INDEXES").
# If you want to manage some indexes manually, move them above the marker line.
# The search.yaml file is automatically uploaded to the admin console when
# you next deploy your application using appcfg.py.\n"""


class VenomIndexGenerator(IndexGenerator):
  yaml_parser = VenomYamlFromFile
  
  def _get_properties_from_schema(self, schema):
    return [
      { 'name': name }
      for name, prop_schema in schema.items()
      if prop_schema.search
    ]
