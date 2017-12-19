from fake_useragent import UserAgent
from mechanicalsoup import StatefulBrowser


class Hoster(object):
    def __init__(self, settings):
        self._browser = self._create_browser()
        self._settings = settings

    def get_configuration(self):
        """Get Hoster configuration.

        :return: Returns configuration for the Hoster instance
        """
        raise NotImplementedError('Abstract method implementation')

    @staticmethod
    def get_gateway():
        """Get payment gateway used by the Hoster.

        :return: Returns the payment gateway module
        """
        raise NotImplementedError('Abstract method implementation')

    @staticmethod
    def get_metadata():
        """Get metadata about the Hoster.

        :return: Returns tuple of name and website url
        """
        raise NotImplementedError('Abstract method implementation')

    @classmethod
    def get_options(cls):
        """Get Hoster options.

        :return: Returns list of Hoster options
        """
        raise NotImplementedError('Abstract method implementation')

    @staticmethod
    def get_required_settings():
        """Get settings required by the Hoster.

        :return: Returns dictionary with sections as keys and the required settings in those sections as values
        """
        raise NotImplementedError('Abstract method implementation')

    def get_status(self):
        """Get Hoster configuration.

        :return: Returns status of the Hoster instance
        """
        raise NotImplementedError('Abstract method implementation')

    def purchase(self, wallet, option):
        """Purchase Hoster.
        
        :param wallet: The Electrum wallet to use for payments
        :param option: Hoster option to purchase
        """
        raise NotImplementedError('Abstract method implementation')

    @staticmethod
    def _create_browser():
        user_agent = UserAgent()
        return StatefulBrowser(user_agent=user_agent.random)
