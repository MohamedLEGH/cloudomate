import time
import re
from selenium import webdriver
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException

from cloudomate import bitcoin_wallet as wallet_util
import sys

class torguard:

    PURCHASE_URL = "https://torguard.net/cart.php?gid=2"
    COINPAYMENTS_URL = "https://www.coinpayments.net/index.php?cmd=checkout"
    driver = None

    # Use this method for purchasing with Bitcoin.
    def purchase_bitcoin(self, user_settings):
        return self._purchase("BTC", user_settings)

    # Use this method for purchasing with Litecoin.
    def purchase_litecoin(self, user_settings):
        return self._purchase("LTC", user_settings)

    # Use this method for purchasing with DASH.
    def purchase_ethereum(self, user_settings):
        return self._purchase("ETH", user_settings)

    #
    def __init__(self):
        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu');
        #driver = webdriver.Chrome(chrome_options=options)
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    # Don't invoke this method directly.
    def _purchase(self, currency, user_settings):
        
        #Get to puchase page
        self.driver.get(self.PURCHASE_URL)
        self.driver.find_element_by_css_selector("button[type='button'][value='Order Now']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button[type='submit'][value='add to cart & checkout »']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button.btn.btn-success").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("input[type='radio'][value='coinpayments']").click()

        time.sleep(1)
        self.driver.find_element_by_css_selector("a[href='/cart.php?a=login']").click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[1]/div/input').send_keys(user_settings.get("email"))
        self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[2]/div/input').send_keys(user_settings.get("password"))

        #Create account
        #self.driver.find_element_by_class_name('email').send_keys(user_settings.get("email"))
        #self.driver.find_element_by_class_name('password').send_keys(user_settings.get("password"))
        #self.driver.find_element_by_class_name('password2').send_keys(user_settings.get("password"))
        #self.driver.find_element_by_class_name('securityqans').send_keys("unknown")

        #Accept terms
        self.driver.find_element_by_id("accepttos").click()
        self.driver.find_element_by_css_selector("input[type='submit'][value='Complete Order »']").click()

        time.sleep(1)

        #Go to coinpayments
        self.driver.find_element_by_id("cpsform").click()
        self.driver.find_element_by_id("coins_" + currency).click()
        self.driver.find_element_by_id("dbtnCheckout").click()
        while not(self.driver.current_url == self.COINPAYMENTS_URL):
            time.sleep(2)

        time.sleep(2)

        amount = ""
        address = ""

        page = self.driver.page_source
        #print(page)
        address_re = '<div><a href="bitcoin:(.*?)?amount=(.*?)">(.*?)</a></div>'

        for line in page.split('\n'):
            match = re.findall(address_re, line)
            if len(match) > 2:
                address = match[0]
                amount = match[1]

        print(address)
        print(amount)

        #Get bitcoin address and amount
        amount = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[1]/div[2]/a').text
        print(amount.split(' ')[0])
        address = self.driver.find_element_by_class_name("address")
        print(address.text)

        instruction = self.driver.find_element_by_xpath('//*[@id="helpa2"]').text
        payment_id = re.findall('transaction ID: (.*?)\n', instruction)
        print(payment_id[0])
        verification_code = re.findall('verification code: (.*?) \(to ', instruction)
        print(verification_code[0])

        #Make purchase
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet_util.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

        return {'amount' : str(amount), 'address' : str(address)}

    def final(self):
        self.driver.get("http://www.ka-wing.nl/scrape")
        amount = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[1]/div[2]/a').text
        print(amount.split(' ')[0])
        address = self.driver.find_element_by_class_name("address")
        print(address.text)

        instruction = self.driver.find_element_by_xpath('//*[@id="helpa2"]').text
        payment_id = re.findall('transaction ID: (.*?)\n', instruction)
        print(payment_id[0])
        verification_code = re.findall('verification code: (.*?) \(to ', instruction)
        print(verification_code[0])

    def re(self):
        text = '<div><a href="bitcoin:36aKgDC3xFMTjxsn8YpcJqtWvyD2Pcp4Rz?amount=0.00114000">0.00114000 BTC</a></div>'
        r = '<div><a href="bitcoin:(.*?)?amount=(.*?)">(.*?)</a></div>'
        match = re.findall(r, text)

        for m in match:
            print(m)


if __name__ == '__main__':
    tg = torguard()
    user_settings = {"email" : "ralphie_obswest@hotmail.com", "password" : "Chicker1$"}
    tg.purchase_bitcoin(user_settings)
    #tg.final()
    #tg.re()