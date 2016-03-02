import os
import fnmatch


def import_all():
  """Imports all py files in the current appengine project"""
  path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
  modules = find_files(path, pattern='*.py')
  for module in modules:
    name = file_to_module(module)
    try:
      __import__(name, globals(), locals(), [], -1)
    except ImportError:
      pass


def find_files(directory, pattern='*'):
  """Finds all files in a given directory matching the given pattern"""
  if not os.path.exists(directory):
    raise ValueError("Directory not found {}".format(directory))

  matches = []
  for root, dirnames, filenames in os.walk(directory):
    
    dirname = os.path.dirname(__file__)
    common_prefix = os.path.commonprefix([dirname, root])
    if common_prefix == dirname: continue
    
    for filename in filenames:
      full_path = os.path.join(root, filename)
      if fnmatch.filter([full_path], pattern):
        matches.append(os.path.join(root, filename))
  
  return matches


def file_to_module(full_path_to_module):
  """Converts a file path to a relative import name with this file as the root"""
  full_path_to_module = os.path.abspath(full_path_to_module)
  common_prefix = os.path.commonprefix([__file__, full_path_to_module])
  relative = os.path.relpath(full_path_to_module, common_prefix)[:-3]
  relative = relative.replace('/', '.')
  return relative