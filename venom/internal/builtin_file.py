# system imports
import os


# threadsafe
def bfile(*args, **kwargs):
  """
  ' This is a factory function that acts as `file(*args, **kwargs)`.
  ' Because app engine's dev_appserver.py sandboxes the __builtin__.file
  ' and __builtin__.open with stubs.FakeFile (line 94 in app engine source)
  ' this function will always return the actual native file object, effecively
  ' circumventing the development sandbox to allow writes in the dev server.
  '
  ' NOTE: In production any writes will obviously fail. The only reason this
  '       is helpful is because the dev server runs on a local machine with
  '       write permissions that are only programatically blocked in python.
  '
  ' NOTE: This fix in particular breaks in Python 3 and above as the file
  '       builtin was removed.
  """
  is_dev = os.environ.get('SERVER_SOFTWARE','').startswith('Development')
  if is_dev and file.__base__ != object:
    file_class = type('file', (file.__base__,), {})
    return file_class(*args, **kwargs)
  return file(*args, **kwargs)