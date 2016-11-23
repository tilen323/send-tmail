#!/usr/bin/env python
import os
import jinja2
import webapp2
from time import gmtime, strftime
from models import *
from google.appengine.api import users


template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), autoescape=False)


class BaseHandler(webapp2.RequestHandler):

    def write(self, *a, **kw):
        return self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        return self.write(self.render_str(template, **kw))

    def render_template(self, view_filename, params=None):
        if not params:
            params = {}
        template = jinja_env.get_template(view_filename)
        return self.response.out.write(template.render(params))


class MainHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()

        logiran = False
        login_url = ""
        logout_url = ""

        if user:
            logiran = True
            user_email = user.email()
            seznam = PosameznoSporocilo.query(PosameznoSporocilo.prejemnik == user_email).fetch()
            user_nickname = user.nickname()
            if not seznam:
                avto_posiljatelj = "prevolnik.tilen@gmail.com"
                avtomatsko_sporocilo = "Dobrodosli v Tmail aplikaciji! Ker je to avtomaticno sporocilo, prosim da nanj vseeno odgovorite:) Pa lep pozdrav, Tilen"
                datum = strftime("%d.%b.%Y, %H:%M:%S", gmtime())

                posamezno_sporocilo = PosameznoSporocilo(posiljatelj=avto_posiljatelj, prejemnik=user_email, sporocilo=avtomatsko_sporocilo, datum=datum)
                posamezno_sporocilo.put()
            logout_url = users.create_logout_url("/")

        else:
            user_nickname = "neznanec"
            login_url = users.create_login_url("/")

        params = {"logiran": logiran, "login_url": login_url, "logout_url": logout_url, "user_nickname": user_nickname}
        return self.render_template("hello.html", params=params)


class PosljiSporociloHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            user_email = user.email()
            params = {"user_email": user_email}
            return self.render_template("poslji_sporocilo.html", params=params)
        else:
            self.redirect_to("home")

    def post(self):
        user = users.get_current_user()
        user_email = user.email()
        prejemnik = self.request.get("prejemnik")
        sporocilo = self.request.get("sporocilo")
        datum = strftime("%d.%b.%Y, %H:%M:%S", gmtime())

        posamezno_sporocilo = PosameznoSporocilo(posiljatelj=user_email, prejemnik=prejemnik, sporocilo=sporocilo, datum=datum)
        posamezno_sporocilo.put()

        params = {"user_email": user_email, "sporocilo": sporocilo}
        return self.render_template("poslji_sporocilo.html", params=params)

class PrejetaSporocilaHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        seznam = PosameznoSporocilo.query(PosameznoSporocilo.prejemnik == user_email).fetch()

        if user:
            params = {"seznam": seznam}
            return self.render_template("prejeta_sporocila.html", params=params)
        else:
            self.redirect_to("home")

class PoslanaSporocilaHandler(BaseHandler):
    def get(self):
        user = users.get_current_user()
        user_email = user.email()
        seznam = PosameznoSporocilo.query(PosameznoSporocilo.posiljatelj == user_email).fetch()

        if user:
            params = {"seznam": seznam}
            return self.render_template("poslana_sporocila.html", params=params)
        else:
            self.redirect_to("home")

class PosameznoSporociloHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = PosameznoSporocilo.get_by_id(int(sporocilo_id))
        user = users.get_current_user()

        params = {"sporocilo": sporocilo, "user": user}
        return self.render_template("posamezno_sporocilo.html", params=params)

class OdgovoriHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = PosameznoSporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("odgovori.html", params=params)

    def post(self, sporocilo_id):
        p_sporocilo = PosameznoSporocilo.get_by_id(int(sporocilo_id))
        posiljatelj = p_sporocilo.prejemnik
        prejemnik = p_sporocilo.posiljatelj
        sporocilo = self.request.get("sporocilo")
        datum = strftime("%d.%b.%Y, %H:%M:%S", gmtime())

        posamezno_sporocilo = PosameznoSporocilo(posiljatelj=posiljatelj, prejemnik=prejemnik, sporocilo=sporocilo, datum=datum)
        posamezno_sporocilo.put()
        rezultat = "uspesno"

        params = {"rezultat": rezultat, "sporocilo": p_sporocilo}
        return self.render_template("odgovori.html", params=params)

class UrediHandler(BaseHandler):
    def get(self, sporocilo_id):
        sporocilo = PosameznoSporocilo.get_by_id(int(sporocilo_id))

        params = {"sporocilo": sporocilo}
        return self.render_template("uredi.html", params=params)

    def post(self, sporocilo_id):
        sporocilo = self.request.get("sporocilo")
        datum = strftime("%d.%b.%Y, %H:%M:%S", gmtime())

        posamezno_sporocilo = PosameznoSporocilo.get_by_id(int(sporocilo_id))
        posamezno_sporocilo.sporocilo = sporocilo
        posamezno_sporocilo.datum = datum
        posamezno_sporocilo.put()
        self.redirect_to("poslana")


app = webapp2.WSGIApplication([
    webapp2.Route('/', MainHandler, name="home"),
    webapp2.Route('/poslji_sporocilo/', PosljiSporociloHandler),
    webapp2.Route('/prejeta_sporocila/', PrejetaSporocilaHandler),
    webapp2.Route('/poslana_sporocila/', PoslanaSporocilaHandler, name="poslana"),
    webapp2.Route('/sporocilo/<sporocilo_id:\d+>/', PosameznoSporociloHandler),
    webapp2.Route('/odgovori/<sporocilo_id:\d+>/', OdgovoriHandler),
    webapp2.Route('/uredi/<sporocilo_id:\d+>/', UrediHandler),
], debug=True)
