from google.appengine.ext import ndb


class PosameznoSporocilo(ndb.Model):
    posiljatelj = ndb.StringProperty()
    prejemnik = ndb.StringProperty()
    sporocilo = ndb.StringProperty()
    izbrisan = ndb.BooleanProperty(default=False)
    datum = ndb.StringProperty()