import time
import re
from selenium import webdriver
import sys

class torguard:
    PURCHASE_URL = "https://torguard.net/cart.php?gid=2"
    COINPAYMENTS_URL = "https://www.coinpayments.net/index.php?cmd=checkout"
    driver = None

    # Use this method for purchasing with Bitcoin.
    def retrieve_bitcoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["bitcoin", "BTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Use this method for purchasing with Litecoin.
    def retrieve_litecoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["litecoin", "LTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Use this method for purchasing with Ethereum.
    # Retrieving Ethereum at the final page is different than for the other currencies.
    def retrieve_ethereum(self, user_settings):
        try:
            return self._retrieve_payment_info(["ethereum", "ETH"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Used for generating error message.
    def _error_message(self, message):
        return "Error " + str(message) + "Try again. It it still does not work, " \
                                         "website might have been updated, update script."

    def __init__(self):
        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu');
        options.add_argument('window-size=1920,1080');
        self.driver = webdriver.Chrome(chrome_options=options)
        #self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    # Don't invoke this method directly.
    def _retrieve_payment_info(self, currency, user_settings):

        print("Placing an order.")

        # Puts VPN in cart and checks out.
        self.driver.get("http://127.0.0.1")
        #self.driver.get(self.PURCHASE_URL)

        sys.exit(0)

        self.driver.find_element_by_css_selector("button[type='button'][value='Order Now']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button[type='submit'][value='add to cart & checkout »']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button.btn.btn-success").click()
        time.sleep(1)

        # Filing in order form.
        self.driver.find_element_by_css_selector("input[type='radio'][value='coinpayments']").click()
        time.sleep(1)

        # Logs in if already registered, else register.
        if user_settings.get("registered") == "1":
            self.driver.find_element_by_css_selector("a[href='/cart.php?a=login']").click()
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[1]/div/input').\
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[2]/div/input').\
                send_keys(user_settings.get("password"))
        else:
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[1]/div/input').\
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="newpw"]').\
                send_keys(user_settings.get("password"))
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[4]/div/input').\
                send_keys(user_settings.get("password"))
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[6]/div/input').\
                send_keys("Blockchain life")

        self.driver.find_element_by_id("accepttos").click()
        self.driver.find_element_by_css_selector("input[type='submit'][value='Complete Order »']").click()
        time.sleep(1)

        # Set registered to 1 so during any purchase in the future, the script will log in instead of registering.
        if user_settings.get("registered") == "0":
            pass

        print("Retrieving the amount and address.")

        # Continue to the final page.
        self.driver.find_element_by_id("cpsform").click()
        self.driver.find_element_by_id("coins_" + currency[1]).click()
        self.driver.find_element_by_id("dbtnCheckout").click()

        tries = 0
        while not (self.driver.current_url == self.COINPAYMENTS_URL):
            tries = tries + 1
            time.sleep(2)
            if tries > 10:
                raise Exception("You probably already have 3 unfinished transfers with coinpayments.net from within "
                                "the last 24 hours and you therefore cannot create anymore.")

        time.sleep(2)

        amount = ""
        address = ""

        page = self.driver.page_source
        address_re = ""
        amount_re = ""
        if currency[0] == "ethereum":
            address_re = '<div class="address">(.*?)</div>'
            amount_re = "<div>(.*?) ETH</div>"
        else:
            address_re = '<div><a href="' + currency[0] + ':(.*?)\?amount=(.*?)">(.*?)</a></div>'

        # Get address and amount
        if currency[0] == "ethereum":
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match_amount = re.findall(amount_re, line)
                match_address = re.findall(address_re, line)
                if len(match_amount) > 0:
                    amount = match_amount[0]
                if len(match_address) > 0:
                    address = match_address[0]
        else:
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match = re.findall(address_re, line)
                if len(match) > 0:
                    address = match[0][0]
                    amount = match[0][1]

        time.sleep(2)
        return {'amount': str(amount), 'address': str(address)}


if __name__ == '__main__':
    tg = torguard()
    user_settings = {"email": "ralphie_ozxcd@hotmail.com", "password" : "Chicker1$", "registered" : "0"}
    dict = tg.retrieve_ethereum(user_settings)
    print(dict['amount'])
    print(dict['address'])