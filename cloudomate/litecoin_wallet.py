# -*- coding: utf-8 -*-

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request

# library for currency prices
from cryptocompy import price


from mechanicalsoup import StatefulBrowser

AVG_TX_SIZE = 226 # same as bitcoin ?
LITOSHI_TO_LTC = 0.00000001


def determine_currency(text):
    """
    Determine currency of text
    :param text: text cointaining a currency symbol
    :return: currency name of symbol
    """
    # Naive approach, for example NZ$ also contains $
    if '$' in text or 'usd' in text.lower():
        return 'USD'
    elif '€' in text or 'eur' in text.lower():
        return 'EUR'
    else:
        return None


def get_rate(currency="USD"):
    """
    Return price of 1 currency in LTC

    :param currency: currency to convert to
    :return: conversion rate from currency to LTC
    """
    if currency is None:
        return None
    factor = price.get_current_price("LTC",currency)
 
    return 1.0 / factor



def get_rates(currencies):
    """
    Return rates for all currencies to LTC.
    :return: conversion rates from currencies to LTC
    """
    rates = {cur: get_rate(cur) for cur in currencies}
    return rates


def get_price(amount, currency='USD'):
    """
    Convert price from one currency to litcoins
    :param amount: number of currencies to convert
    :param currency: currency to convert from
    :return: price in litcoins
    """
    price = amount * get_rate(currency)
    return price

"""
#function not yet available on Litecoin chain
def _get_network_cost(speed):
    br = StatefulBrowser(user_agent='Firefox')
    #page = br.open('https://bitcoinfees.21.co/api/v1/fees/recommended')
    response = page.json()
    satoshirate = float(response[speed])
    return satoshirate
"""

def get_network_fee():
    """
    Give an estimate of network fee for the average litecoin transaction for given speed.
    Supported speeds are available at https://bitcoinfees.21.co/api/v1/fees/recommended
    :return: network cost
    """
    #network_fee = _get_network_cost(speed) * SATOSHI_TO_BTC
    # 0.0002 LTC is the standard transaction fee
    return 0.0002


class Wallet:
    """
    Wallet implements an adapter to the wallet handler.
    Currently Wallet only supports electrum-ltc wallets without passwords for automated operation.
    Wallets with passwords may still be used, but passwords will have to be entered manually.
    """

    def __init__(self, wallet_command=None, wallet_path=None):
        if wallet_command is None:
            if os.path.exists('/usr/local/bin/electrum-ltc'):
                wallet_command = ['/usr/local/bin/electrum-ltc']
            else:
                wallet_command = ['/usr/bin/env', 'electrum-ltc']
        self.command = wallet_command
        self.wallet_handler = electrum-ltcWalletHandler(wallet_command, wallet_path)

    def get_balance(self, confirmed=True, unconfirmed=True):
        """
        Return the balance of the default electrum-ltc wallet
        Confirmed and unconfirmed can be set to indicate which balance to retrieve.
        :param confirmed: default: True
        :param unconfirmed: default: True
        :return: balance of default wallet
        """
        balance_output = self.wallet_handler.get_balance()
        balance = 0.0
        if confirmed:
            balance = balance + float(balance_output.get('confirmed', 0.0))
        if unconfirmed:
            balance = balance + float(balance_output.get('unconfirmed', 0.0))
        return balance

    def get_balance_confirmed(self):
        """
        Return confirmed balance of default electrum-ltc wallet
        :return: 
        """
        return self.get_balance(confirmed=True, unconfirmed=False)

    def get_balance_unconfirmed(self):
        """
        Return unconfirmed balance of default electrum-ltc wallet
        :return: 
        """
        return self.get_balance(confirmed=False, unconfirmed=True)

    def get_addresses(self):
        """
        Return the list of addresses of the default electrum-ltc wallet
        :return: 
        """
        address_output = self.wallet_handler.get_addresses()
        return address_output

    def pay(self, address, amount, fee=None):
        tx_fee = 0 if fee is None else fee
        if self.get_balance() < amount + tx_fee:
            print('Not enough funds')
            return
        transaction_hex = self.wallet_handler.create_transaction(amount, address, fee)
        success, transaction_hash = self.wallet_handler.broadcast(transaction_hex)
        if not success:
            print(('Transaction not successfully broadcast, do error handling: {0}'.format(transaction_hash)))
        else:
            print('Transaction successful')
        print(transaction_hex)
        print(success)
        print(transaction_hash)
        return transaction_hash


class electrum-ltcWalletHandler(object):
    """
    electrum-ltcWalletHandler ensures the correct opening and closing of the electrum-ltc wallet daemon
    """

    def __init__(self, wallet_command=None, wallet_path=None):
        """
        Allows wallet_command to be changed to for example electrum-ltc --testnet
        :param wallet_command: command to call wallet
        """
        if wallet_command is None:
            if os.path.exists('/usr/local/bin/electrum-ltc'):
                wallet_command = ['/usr/local/bin/electrum-ltc']
            else:
                wallet_command = ['/usr/bin/env', 'electrum-ltc']
        self.command = wallet_command
        p, e = subprocess.Popen(self.command + ['daemon', 'status'], stdout=subprocess.PIPE).communicate()
        self.not_running_before = b'not running' in p
        if self.not_running_before:
            subprocess.call(self.command + ['daemon', 'start'])
        if wallet_path is None:
            subprocess.call(self.command + ['daemon', 'load_wallet'])
        else:
            print('Using wallet: ', wallet_path)
            subprocess.call(self.command + ['daemon', 'load_wallet', '-w', wallet_path])

    def __del__(self):
        if self.not_running_before:
            subprocess.call(self.command + ['daemon', 'stop'])

    def create_transaction(self, amount, address, fee):
        """
        Create a transaction
        :param amount: amount of litcoins to be transferred
        :param address: address to transfer to
        :param fee: None for autofee, or specify own fee
        :return: transaction details
        """
        if fee is None:
            transaction = subprocess.check_output(self.command + ['payto', str(address), str(amount)]).decode()
        else:
            transaction = subprocess.check_output(self.command + ['payto', str(address), str(amount), '-f', str(fee)]).decode()
        jtrs = json.loads(transaction)
        return jtrs['hex']

    def broadcast(self, transaction):
        """
        Broadcast a transaction
        :param transaction: hex of transaction
        :return: if successful returns success and
        """
        broadcast = subprocess.check_output(self.command + ['broadcast', transaction]).decode()
        jbr = json.loads(broadcast)
        return tuple(jbr)

    def get_balance(self):
        """
        Return the balance of the default electrum-ltc wallet
        :return: balance of default wallet
        """
        output = subprocess.check_output(self.command + ['getbalance']).decode()
        balance_dict = json.loads(output)
        return balance_dict

    def get_addresses(self):
        """
        Return the list of addresses of default wallet
        :return: 
        """
        address = subprocess.check_output(self.command + ['listaddresses']).decode()
        addr = json.loads(address)
        return addr
