import venom


app = venom.Application()


import user


class Trip(venom.Model):
  name = venom.Properties.String(min=1)
  created = venom.Properties.DateTime(set_on_creation=True)


class Waypoint(venom.Model):
  name = venom.Properties.String(min=1)
  latitude = venom.Properties.Float(min=-90, max=90)
  longitude = venom.Properties.Float(min=-180, max=180)


app.CRUD('/trips', Trip).domain.headers({
  'User': user.UserAuthProperty()
})

app.CRUD('/trips/:trip/waypoints', Waypoint).domain.url({
  'trip': venom.Properties.Model(Trip, required=True)
}).headers({
  'User': user.UserAuthProperty()
})
