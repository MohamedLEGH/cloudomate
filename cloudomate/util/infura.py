from robobrowser import RoboBrowser
from cloudomate.util.recaptchasolver import reCaptchaSolver
import re
import random

class Infura:
    h = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"
    br = RoboBrowser(parser='html.parser', history=True, user_agent=h)

    def randomGenerator(self, length=0):
        if length is 0:
            length = random.randrange(4, 15)

        possibilities = "abcdefghijklmnopqrstuvwxyz"
        temp = ""

        for i in range(0, length):
            temp = temp + possibilities[random.randrange(len(possibilities))]

        return temp

    def register(self):
        registration = "https://form.infura.io/form/embed.php?id=11217"
        self.br.open(registration)

        # Gets the Google Recaptcha key and the solution hash.
        datasitekey = str(self.br.find(attrs="g-recaptcha")).split('"')[3]
        captchasolver = reCaptchaSolver("fd58e13e22604e820052b44611d61d6c")
        solution = captchasolver.solveGoogleReCaptcha(registration, datasitekey)

        # Post data
        form = self.br.get_form()
        key = form['element_4'].value
        data = {"element_3_1" : self.randomGenerator(0),
                "element_3_2" : self.randomGenerator(0),
                "element_2" : self.randomGenerator(0) + "@" + self.randomGenerator(0) + "." + self.randomGenerator(length=3),
                "element_4" : key,
                "element_13" : "",
                "element_14" : "",
                "element_12" : "",
                "element_7" : "",
                "element_8" : "",
                "element_9_other" : "",
                "element_15" : "",
                "element_17" : "",
                "element_18_1" : "1",
                "g-recaptcha-response" : solution,
                "form_id" : "11217",
                "submit_form" : "1",
                "page_number" : "1"
                }

        # Use the post method on the given link.
        response = self.br.session.post("https://form.infura.io/form/embed.php", data)

        # Checks if registration went wrong
        for line in response.text.split("\n"):
            if("error_message" in line):
                raise Exception("Something went wrong during registration."
                                "Might be incorrect Captcha solution. Try again.")

        # Gets the redirection link
        link = str(response.text).split("'")[1]

        # If registration link does not match as expected.
        if not re.match("https\:\/\/infura.io/setup\?key=", link):
            raise Exception("Return link does not match as expected")
        else:
            return  {'Mainnet': 'https://mainnet.infura.io/' + key,
                     'Ropsten': 'https://ropsten.infura.io/' + key}