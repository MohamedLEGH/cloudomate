from cloudomate.hoster.hoster import Hoster
from cloudomate import wallet as wallet_util
from collections import namedtuple

import sys

VpnConfiguration = namedtuple('VpnConfiguration', ['username', 'password', 'ovpn'])
VpnOption = namedtuple('VpnOption', ['name', 'protocol', 'price', 'bandwidth', 'speed'])  # Price in USD
VpnStatus = namedtuple('VpnStatus', ['online', 'expiration'])   # Online is a boolean, expiration an ISO datetime

class VpnHoster(Hoster):
    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns VpnConfiguration for the VPN Hoster instance
        """
        raise NotImplementedError('Abstract method implementation')

    @classmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of VpnOption objects
        """
        raise NotImplementedError('Abstract method implementation')

    def get_status(self):
        """Get Hoster configuration.

        :return: Returns VpnStatus of the VPN Hoster instance
        """
        raise NotImplementedError('Abstract method implementation')


    """
    Legacy methods
    Still used by the commandline
    Remove when possible
    """

    def get_status(self):
        # Backward compatibility, apparently this method should print and not return the values
        row = "{:18}" * 2
        status = self.get_status(self.settings)
        print(row.format("Online", "Expiration"))
        print(row.format(str(status.online), status.expiration.isoformat()))

    def print_options(self, options):
        bandwidth = "Unlimited" if options.bandwidth == sys.maxsize else options.bandwidth
        speed = "Unlimited" if options.speed == sys.maxsize else options.speed

        # Calculate the estimated price
        rate = wallet_util.get_rate("USD")
        fee = wallet_util.get_network_fee()
        estimate = self.gateway.estimate_price(options.price * rate) + fee  # BTC
        estimate = round(1000 * estimate, 2)  # mBTC

        # Print everything
        row = "{:18}" * 6
        print(row.format("Name", "Protocol", "Bandwidth", "Speed", "Est. Price (mBTC)", "Price (USD)"))
        print(row.format(options.name, options.protocol, bandwidth, speed, str(estimate), str(options.price)))

    # For compatibility with the commandline code
    def print_configurations(self):
        options = self.get_options()
        self.print_options(options)
