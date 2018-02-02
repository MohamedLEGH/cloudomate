import time
import re
from selenium import webdriver

class torguard:

    PURCHASE_URL = "https://torguard.net/cart.php?gid=2"
    COINPAYMENTS_URL = "https://www.coinpayments.net/index.php?cmd=checkout"

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
        driver = webdriver.Chrome()
        driver.maximize_window()

    # Don't invoke this method directly.
    def _purchase(self, currency, user_settings):
        
        #Get to puchase page
        driver.get(PURCHASE_URL)
        driver.find_element_by_css_selector("btn btn-primary").click()
        driver.find_element_by_css_selector("btn btn-primary").click()
        driver.find_element_by_css_selector("btn btn-success").click()
        driver.find_elements_by_class_name("paymentmethod").select_by_value("coinpayments").click()


        #Create account
        driver.find_element_by_class_name('email').send_keys(user_settings.get("email"))
        driver.find_element_by_class_name('password').send_keys(user_settings.get("password"))
        driver.find_element_by_class_name('password2').send_keys(user_settings.get("password"))
        driver.find_element_by_class_name('securityqans').send_keys("unknown")

        #Accept terms
        driver.find_element_by_id("accepttos").click()
        driver.find_element_by_css_selector("btn btn-success btn-lgs").click()



        #Go to coinpayments
        driver.find_element_by_id("cpsform").click()
        driver.find_element_by_id("coins_" + currency).click()
        driver.find_element_by_id("dbtnCheckout").click()
        while driver.current_url() != COINPAYMENTS_URL:
            time.sleep(2)

        #Get bitcoin address and amount
        amount = driver.find_element_by_class_name("address").text
        address = driver.find_element_by_class_name("w-col w-col-3").find_elements_by_class_name("sc2-label").find_element_by_tag_name("div").text.split(" ")[0]

        #Make purchase
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

        return {'amount' : str(amount), 'address' : str(address)}

if __name__ == '__main__':
    tg = torguard()
    user_settings = {"email" : "chicker@tudelft.nl", "password" : "hoihoihoi1$"}
    tg.purchase_bitcoin()