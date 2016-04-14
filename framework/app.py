import venom

from routes import version1
from routes import version2


app = venom.VersionDispatch(version1, version2)
