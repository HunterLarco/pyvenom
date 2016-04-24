import venom

from routes import version1


app = venom.VersionDispatch(version1)
