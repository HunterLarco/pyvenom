from google.appengine.ext import vendor
import os

# Add any libraries installed in the "vendor" folder.
path = os.path.join(os.path.dirname(__file__), 'vendor')
vendor.add(path)