import venom


app = venom.Application()


class Trip(venom.Model):
  name = venom.Properties.String(min=1, required=True)


class Waypoint(venom.Model):
  name = venom.Properties.String(min=1, required=True)
  location = venom.Properties.Location(required=True)
  trip = venom.Properties.Model(Trip, required=True)
  
  by_trip = venom.Query(trip == venom.QP)
  nearme = venom.Query(location.distance_to(45, 78) < 100)


app.CRUD('/trips', Trip)
app.CRUD('/waypoints', Waypoint)