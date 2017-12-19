from cloudomate.hoster.vps.clientarea import ClientArea
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.util.config import UserOptions
from mechanicalsoup import StatefulBrowser

class ClientAreaFingerprinter(object):

    def __init__(self, clientarea_url, user_settings):
        self.br = StatefulBrowser()
        self.user_settings = UserOptions()
        self.user_settings.read_settings(user_settings)
        self.clientarea_url = clientarea_url

    def attemptLogin(self):

        self.br.open(self.clientarea_url)
        self.br.select_form('.logincontainer form')
        self.br['username'] = self.user_settings.get('email')
        self.br['password'] = self.user_settings.get('password')
        page = self.br.submit_selected()
        if "incorrect=true" in page.url:
            return False
        else:
            return True

    def register(self):
        self.br.follow_link('register')
        self.br.select_form('form[action="/billing/register.php"]')

        self.br['firstname'] = self.user_settings.get("firstname")
        self.br['lastname'] = self.user_settings.get("lastname")
        self.br['email'] = self.user_settings.get("email")
        self.br['phonenumber'] = self.user_settings.get("phonenumber")
        self.br['companyname'] = self.user_settings.get("companyname")
        self.br['address1'] = self.user_settings.get("address")
        self.br['city'] = self.user_settings.get("city")
        self.br['state'] = self.user_settings.get("state")
        self.br['postcode'] = self.user_settings.get("zipcode")
        self.br['country'] = self.user_settings.get('countrycode')
        self.br['password'] = self.user_settings.get("password")
        self.br['password2'] = self.user_settings.get("password")
        self.br['accepttos'] = True

        self.br.submit_selected()
2

testfp = ClientAreaFingerprinter(LegionBox.clientarea_url, '/home/tom/.config/cloudomatetest.cfg')
loggedin = testfp.attemptLogin()

if not(loggedin):
    testfp.register()

testfp.br.launch_browser()