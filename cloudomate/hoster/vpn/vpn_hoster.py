from cloudomate.hoster.hoster import Hoster


class VpnHoster(Hoster):
    """
    Abstract class for VPN Hosters, concrete classes should provide the information in the __init__ function.
    """

    def __init__(self):
        super(VpnHoster, self).__init__()

        self.name = None
        self.protocol = None
        self.price = None
        self.bandwidth = None
        self.speed = None

    def purchase(self, user_settings, wallet):
        """
        This function should actually buy a vps server with the specified wallet and provided credentials.
        """
        raise NotImplementedError('Abstract method implementation')

    def options(self):
        return {
            'name': self.name,
            'protocol': self.protocol,
            'price': self.price,
            'bandwidth': self.bandwidth,
            'speed': self.speed,
        }
