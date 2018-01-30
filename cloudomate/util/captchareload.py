import time
import re
from selenium import webdriver

class anticaptcha:

    username = ""
    password = ""

    # Use this method for purchasing with Bitcoin.
    def purchase_bitcoin(self, amount=10):
        return self.purchase(["Bitcoin", "BTC", "btc"], amount)

    # Use this method for purchasing with Litecoin.
    def purchase_litecoin(self, amount=10):
        return self.purchase(["Litecoin", "LTC", "ltc"], amount)

    # Use this method for purchasing with DASH.
    def purchase_dash(self, amount=10):
        return self.purchase(["DASH", "DASH", "dash"], amount)

    # Don't invoke this method directly.
    def purchase(self, currency, amount=10):
        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu');
        options.add_argument('window-size=1920,1080');
        driver = webdriver.Chrome(chrome_options=options)
        driver.maximize_window()

        #Logs in
        driver.get("https://anti-captcha.com/clients/entrance/login")
        driver.find_element_by_id('enterlogin').send_keys(self.username)
        driver.find_element_by_id('password').send_keys(self.password)
        driver.find_element_by_css_selector("button.btn.btn-primary").click()
        time.sleep(2)

        # Clicking menu
        print("Click Finance")
        driver.find_element_by_id("menu2").find_element_by_class_name("head").click()
        time.sleep(2)
        print("Click Add Funds")
        driver.find_element_by_id("menu2").find_element_by_class_name("submenu").\
            find_element_by_tag_name("li").find_element_by_tag_name("a").click()
        time.sleep(2)

        # Choosing cryptocurrency as payment option
        payment_methods = driver.find_element_by_id("listSection").find_elements_by_class_name("col")
        for payment_method in payment_methods:
            text = payment_method.find_element_by_tag_name("a").get_attribute("action-parameter")
            if text == "Bitcoins":
                payment_method.click()
                print("Click cryptocurrency")
                break

        time.sleep(2)

        # Choosing the correct cryptocurrency.
        cryptocurrencies = driver.find_elements_by_class_name("grid-middle")
        for c in cryptocurrencies:
            text = c.find_element_by_class_name("col")
            if text is not None:
                if currency[0] in text.text:
                    button = c.find_element_by_class_name("col-3_xs-12")
                    button = button.find_element_by_css_selector("a.btn.btn-primary.btn-manager")
                    print("Click Select " + currency[0])
                    button.click()
                    break

        time.sleep(2)

        # Filling in the amount.
        print("Filling in $" + str(amount) + ".")
        form = driver.find_element_by_id("amountInput")
        form.clear()
        for i in range(0, len(str(amount))): # Because of a small bug, the numbers need to be send one by one.
            form.send_keys(str(amount)[i])
        time.sleep(1)
        print("Click Pay.")
        driver.find_element_by_id("paymentButton").find_element_by_css_selector("button.btn.btn-primary.btn-manager")\
            .click()

        # Waiting for status to become "waiting for transaction"
        print("Requesting status.")
        while(True):
            time.sleep(3)
            status = driver.find_element_by_id(currency[2]+"status")
            if status.text == "Status: waiting for transaction":
                print("Done waiting")
                break

        # Finds Address
        address = driver.find_element_by_id("customSection")
        address = address.find_element_by_css_selector("div.tac.font24").text

        # Finds Amount
        instructions = driver.find_element_by_id("customSection").find_element_by_css_selector("div.desc").\
            find_element_by_tag_name("div")
        amount = re.findall("send (.*?)" + currency[1] + " to", instructions.text)[0]

        return {'amount' : str(amount), 'address' : str(address)}
