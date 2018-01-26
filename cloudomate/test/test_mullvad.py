import unittest
from mock import patch,MagicMock,Mock
from cloudomate.hoster.vpn.mullvad import MullVad
from cloudomate.util.config import UserOptions
import datetime
from cloudomate.wallet import Wallet

class TestMullvad(unittest.TestCase):
     
    def setUp(self):
        self.mullvad = MullVad()
        self.user_settings = MagicMock(UserOptions)
        self.wallet = MagicMock(Wallet)

    def test_purchase(self):
        self.mullvad._register = MagicMock()
        self.mullvad._order = MagicMock(return_value=(0.0040, '1Teads546422'))
        
        self.mullvad.purchase(self.user_settings, self.wallet)
        
        assert self.mullvad._register.called_once_with(self.mullvad, self.user_settings, self.wallet)
        assert self.mullvad._order.called_once_with(self.mullvad, self.user_settings, self.wallet)


    def test_status(self):
        self.mullvad._checkVPNDate = MagicMock(return_value=(True,'-5'))
        self.mullvad._login = MagicMock()

        expiration_date = self.mullvad.status(self.user_settings)[1]
        now = datetime.datetime.now(datetime.timezone.utc)
        expiration_days = datetime.timedelta(days=int('-5'))
        full_date = now + expiration_days

        self.assertEqual(expiration_date.day, full_date.day)
        self.assertEqual(expiration_date.month, full_date.month)

    @patch('time.sleep')
    @patch('os.chdir')
    @patch('os.popen')
    def test_setup(self, mock1, mock2, mock3):
        self.mullvad._downloadFiles = MagicMock()
        self.mullvad._checkVPN = MagicMock()
        
        self.mullvad.setupVPN()

        assert self.mullvad._downloadFiles.called_once_with(self.mullvad)
        assert self.mullvad._checkVPN.called_once_with(self.mullvad,True)

