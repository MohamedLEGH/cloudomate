import unittest

from parameterized import parameterized
from mock.mock import MagicMock

from cloudomate.hoster.vps.blueangelhost import BlueAngelHost
from cloudomate.hoster.vps.ccihosting import CCIHosting
from cloudomate.hoster.vps.crowncloud import CrownCloud
from cloudomate.hoster.vps.legionbox import LegionBox
from cloudomate.hoster.vps.linevast import LineVast
from cloudomate.hoster.vps.pulseservers import Pulseservers
from cloudomate.hoster.vps.undergroundprivate import UndergroundPrivate

from cloudomate.util.fakeuserscraper import UserScraper

providers = [
    (BlueAngelHost,),
    (CCIHosting,),
    (CrownCloud,),
    (LegionBox,),
    (LineVast,),
    (Pulseservers,),
    (UndergroundPrivate,),
]


class TestHosters(unittest.TestCase):
    @parameterized.expand(providers)
    def test_hoster_implements_interface(self, hoster):
        self.assertTrue('options' in dir(hoster), msg='options is not implemented in {0}'.format(hoster.name))
        self.assertTrue('purchase' in dir(hoster), msg='purchase is not implemented in {0}'.format(hoster.name))

    @parameterized.expand(providers)
    def test_hoster_options(self, hoster):
        options = hoster().start()
        self.assertTrue(len(list(options)) > 0)

    @parameterized.expand(providers)
    def test_hoster_purchase(self, hoster):
        user_settings = UserScraper().get_user()
        host = hoster()
        options = list(host.start())[0]
        wallet = MagicMock()
        wallet.pay = MagicMock()

        host.purchase(user_settings, options, wallet)

        wallet.pay.assert_called_once()


if __name__ == '__main__':
    unittest.main()
