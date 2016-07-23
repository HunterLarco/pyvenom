import types
import imputil


def handle_blueprint_import(filename, finfo, fqname):
  print filename, finfo, fqname
  module_name = fqname.split('.')[-1]
  
  is_pkg = 0
  code = types.ModuleType('')
  values = { '__file__' : filename }
  return is_pkg, code, values


fs = imputil._FilesystemImporter()
fs.add_suffix('.blueprint', handle_blueprint_import)

# TODO(hunterlarco) Find 2.7 alternative
# Will conflict if other libraries do the same
# (deprecated in 2.5)
manager = imputil.ImportManager(fs_imp=fs)
# manager.install()
