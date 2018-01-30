from cloudomate.hoster.vpn.vpn_hoster import VpnHoster
from cloudomate.hoster.vpn.vpn_hoster import VpnStatus
from cloudomate.hoster.vpn.vpn_hoster import VpnInfo
from cloudomate.gateway import bitpay
from cloudomate import bitcoin_wallet as wallet_util
from forex_python.converter import CurrencyRates
import sys
import re
import datetime
import requests

class ExpressVpn(VpnHoster):
    REGISTER_URL = "https://www.expressvpn.com/order"

    required_settings = [
        'email',
    ]

    def __init__(self):
        super().__init__()

        self.name = "ExpressVPN"
        self.website = "https://www.expressvpn.com/order"
        self.protocol = "OpenVPN"
        self.bandwidth = sys.maxsize
        self.speed = sys.maxsize

        self.gateway = bitpay

    def options(self):
        self.br.open(self.REGISTER_URL)
        soup = self.br.get_current_page()
        strong = soup.select("div.prices > ul > li:nth-of-type(2) > ul > li:nth-of-type(1) strong")
       	textValue = soup.select("div.wrapper > div.content > div.click_off_alerts > form.new_signup > div:nth-of-type(3) > div.row > div:nth-of-type(2) > div.plan > div.plan-box > div.plan-amount > div.price > div.monthly-amount")[0].text
        #priceVPN = float(re.search(r'\d+\.\d+',textValue).group())
        self.price = float(textValue)

        return super().options()

    def purchase(self, user_settings, wallet):
        # Prepare for the purchase on the ExpressVPN website

        page = self._order(user_settings)

        # Make the payment
        print("Purchasing ExpressVPN instance")
        amount, address = self.gateway.extract_info(page.url)
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

    def info(self, user_settings):
        response = requests.get(self.REGISTER_URL)
        ovpn = response.text
        return VpnInfo(user_settings.get("email"), ovpn)

    def status(self, user_settings):
        self._login(user_settings)

        # Retrieve the expiration date
        self.br.open(self.REGISTER_URL)
        soup = self.br.get_current_page()
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
        return VpnStatus(online, expiration)


    def _order(self, user_settings):
        #Register with email and choose 1 month plan
        self.br.open(self.REGISTER_URL)
        form = self.br.select_form()
        #print(form.print_summary())
        form["signup[package_id]"] = "1"
        form["signup[payment_method]"] = "5"
        form["signup[email]"] = user_settings.get("email")
        form["commit"] = "Continue to BitPay"
        self.br.submit_selected()
        #Go to redirect page with wait_for parameter
        wait_for = str(self.br.get_url()).split("&")[2]
        redirect_page = self.br.open("https://www.expressvpn.com/signup/waiting?"+wait_for)
        #Get the url for bitpayment from the (second) redirect page and open it
        #print(self.br.get_url())
        page = self.br.open(redirect_page.text.split(":", 1)[1].split('"')[1])
        print(self.br.get_url())
        #print(page.text)
        return page

if __name__ == '__main__':
    ev = ExpressVpn()
    user_settings = {"email" : "chicker@tudelft.nl"}
    ev.purchase(user_settings)