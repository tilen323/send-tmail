from google.appengine.ext import ndb


class PosameznoSporocilo(ndb.Model):
    posiljatelj = ndb.StringProperty()
    prejemnik = ndb.StringProperty()
    sporocilo = ndb.StringProperty()
    izbrisan = ndb.BooleanProperty(default=False)
    prebran = ndb.BooleanProperty(default=False)
    datum = ndb.DateTimeProperty(auto_now_add=True)