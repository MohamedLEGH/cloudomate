from cloudomate import wallet as wallet_util
from cloudomate.gateway import bitpay
from cloudomate.hoster.vpn import vpn_hoster
import datetime
from forex_python.converter import CurrencyRates
import requests
import sys


class AzireVpn(vpn_hoster.VpnHoster):
    REGISTER_URL = "https://manager.azirevpn.com/en/auth/register"
    CONFIGURATION_URL = "https://www.azirevpn.com/support/configuration/generate?os=others&country=se1&nat=0&keys=0&protocol=udp&tls=gcm&port=random"
    LOGIN_URL = "https://manager.azirevpn.com/auth/login"
    ORDER_URL = "https://manager.azirevpn.com/order"
    OPTIONS_URL = "https://www.azirevpn.com"
    DASHBOARD_URL = "https://manager.azirevpn.com"


    '''
    Information about the Hoster
    '''

    @staticmethod
    def get_gateway():
        return bitpay

    @staticmethod
    def get_metadata():
        return ("AzireVPN", "https://www.azirevpn.com")

    @staticmethod
    def get_required_settings():
        return {"user", ["username", "password"]}


    '''
    Action methods of the Hoster that can be called
    '''

    def get_configuration(self):
        response = requests.get(self.CONFIGURATION_URL)
        ovpn = response.text
        return vpn_hoster.VpnInfo(self.settings.get("username"), self.settings.get("password"), ovpn)

    @classmethod
    def get_options(cls):
        # Get string with price from the website
        self._browser.open(self.OPTIONS_URL)
        soup = self._browser.get_current_page()
        strong = soup.select_one("div.prices > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) strong")
        string = strong.get_text()
        eur = float(string[string.index("€")+2 : string.index("/")-1])

        # Calculate the price in USD
        c = CurrencyRates()
        usd = c.convert("EUR", "USD", eur)
        usd = round(usd, 2)
        price = usd

        name, _ = self.get_metadata()
        option = vpn_hoster.VpnOption(name, "OpenVPN", price, sys.maxsize, sys.maxsize)
        return [option]

    def get_status(self):
        self._login()

        # Retrieve the expiration date
        self._browser.open(self.DASHBOARD_URL)
        soup = self._browser.get_current_page()
        time = soup.select_one("div.dashboard time")
        d = time["datetime"]

        # Parse the expiration date
        d = d[0:-3] + d[-2:]  # Remove colon (:) in timezone
        expiration = datetime.datetime.strptime(d, "%Y-%m-%dT%H:%M:%S%z")

        # Determine the status
        now = datetime.datetime.now(datetime.timezone.utc)
        online = False
        if now <= expiration:
            online = True
        return vpn_hoster.VpnStatus(online, expiration)

    def purchase(self, wallet, option):
        # Prepare for the purchase on the AzireVPN website
        self._register()
        self._login()
        page = self._order()

        # Make the payment
        print("Purchasing AzireVPN instance")
        amount, address = self.gateway.extract_info(page.url)
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash


    '''
    Hoster-specific methods that are needed to perform the actions
    '''

    def _register(self):
        self._browser.open(self.REGISTER_URL)
        form = self._browser.select_form()
        form["username"] = self.settings.get("username")
        form["password"] = self.settings.get("password")
        form["password_confirmation"] = self.settings.get("password")
        #form["email"] = self.settings.get("email")
        page = self._browser.submit_selected()

        if page.url == self.REGISTER_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _login(self):
        self._browser.open(self.LOGIN_URL)
        form = self._browser.select_form()
        form["username"] = self.settings.get("username")
        form["password"] = self.settings.get("password")
        page = self._browser.submit_selected()

        if page.url == self.LOGIN_URL:
            # An error occurred
            soup = self._browser.get_current_page()
            ul = soup.select_one("ul.alert-danger")
            print(ul.get_text())
            sys.exit(2)

        return page

    def _order(self):
        self._browser.open(self.ORDER_URL)
        form = self._browser.select_form("form#orderForm")
        form["package"] = "1"
        form["payment_gateway"] = "bitpay"
        form["tos"] = True
        page = self._browser.submit_selected()

        return page
