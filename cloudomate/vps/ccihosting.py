from collections import OrderedDict

from bs4 import BeautifulSoup

from cloudomate.gateway import coinbase
from cloudomate.vps.clientarea import ClientArea
from cloudomate.vps.solusvm_hoster import SolusvmHoster
from cloudomate.vps.vpsoption import VpsOption
from cloudomate.wallet import determine_currency


class CCIHosting(SolusvmHoster):
    name = "ccihosting"
    website = "http://www.ccihosting.com/"
    clientarea_url = "https://www.ccihosting.com/accounts/clientarea.php"
    required_settings = [
        'firstname',
        'lastname',
        'email',
        'phonenumber',
        'address',
        'city',
        'countrycode',
        'state',
        'zipcode',
        'password',
        'hostname',
        'rootpw'
    ]
    gateway = coinbase

    def __init__(self):
        super(CCIHosting, self).__init__()

    def register(self, user_settings, vps_option):
        """
        Register CCIHosting provider, pay through 
        :param user_settings: 
        :param vps_option: 
        :return: 
        """
        self.br.open(vps_option.purchase_url)
        self.server_form(user_settings)
        self.br.open('https://www.ccihosting.com/accounts/cart.php?a=confdomains')
        self.br.follow_link(text_regex="Checkout")
        self.br.select_form(nr=2)
        self.user_form(self.br, user_settings, self.gateway.name)
        self.br.select_form(nr=0)
        coinbase_url = self.br.form.attrs.get('action')
        return self.gateway.extract_info(coinbase_url)

    def server_form(self, user_settings):
        """
        Fills in the form containing server configuration
        :param user_settings: settings
        :return: 
        """
        self.select_form_id(self.br, 'frmConfigureProduct')
        self.fill_in_server_form(self.br.form, user_settings)
        self.br.form['configoption[214]'] = ['1193']  # Ubuntu
        self.br.submit()

    def start(self):
        self.br.open('https://www.ccihosting.com/offshore-vps.html')
        return self.parse_options(self.br.get_current_page())

    def parse_options(self, page):
        tables = page.findAll('div', class_='p_table')
        for column in tables:
            yield self.parse_cci_options(column)

    @staticmethod
    def parse_cci_options(column):
        header = column.find('div', class_='phead')
        price = column.find('span', class_='starting-price')
        info = column.find('ul').findAll('li')
        return VpsOption(
            name=header.find('h2').contents[0],
            price=float(price.contents[0]),
            currency=determine_currency(price.previous_sibling.strip()),
            cpu=int(info[1].find('strong').contents[0]),
            ram=float(info[2].find('strong').contents[0]),
            storage=float(info[3].find('strong').contents[0]),
            bandwidth=info[4].find('strong').contents[0].lower(),
            connection=10,
            purchase_url=column.find('a')['href']
        )

    def get_status(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.print_services()

    def set_rootpw(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        clientarea.set_rootpw_rootpassword_php()

    def get_ip(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        return clientarea.get_ip()

    def info(self, user_settings):
        clientarea = ClientArea(self.br, self.clientarea_url, user_settings)
        data = clientarea.get_service_info()
        return OrderedDict([
            ('Hostname', data[0]),
            ('IP address', data[1]),
            ('Nameservers', data[2]),
        ])
