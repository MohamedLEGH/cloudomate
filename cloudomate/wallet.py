# -*- coding: utf-8 -*-

import json
import os
import subprocess
import urllib.error
import urllib.parse
import urllib.request

from mechanicalsoup import StatefulBrowser

# library for currency prices
from cryptocompy import price

# library used for ethereum
import rlp 

from web3 import Web3, HTTPProvider, IPCProvider
from ethereum.transactions import Transaction


NB_GAS_FOR_TRANSACTION = 21000
# get gas price in gas station ??

ETHER_TO_WEI=1000000000000000000
WEI_TO_ETHER=0.000000000000000001

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
    Return price of 1 currency in ETH

    :param currency: currency to convert to
    :return: conversion rate from currency to ETH
    """
    if currency is None:
        return None
    factor = price.get_current_price("ETH",currency)
 
    return 1.0 / factor

def get_rates(currencies):
    """
    Return rates for all currencies to ETH.
    :return: conversion rates from currencies to ETH
    """
    rates = {cur: get_rate(cur) for cur in currencies}
    return rates


def get_price(amount, currency='USD'):
    """
    Convert price from one currency to ether
    :param amount: number of currencies to convert
    :param currency: currency to convert from
    :return: price in ether
    """
    price = amount * get_rate(currency)
    return price

def get_network_fee(): # with web3.py he gives 520 gwei which is too much
    """
    Give an estimate of network fee for a simple ether transaction.
    from http://gasprice.dopedapp.com/
    :return: network cost
    """
    br = StatefulBrowser(user_agent='Firefox')
    page = br.open('http://gasprice.dopedapp.com/')
    response = page.json()
    gwei_cost = float(response['safe_price_in_gwei'])
    return gwei_cost


class Wallet:
    """
    Wallet implements an adapter to the wallet handler.
    Currently Wallet only supports electrum wallets without passwords for automated operation.
    Wallets with passwords may still be used, but passwords will have to be entered manually.
    """

    def __init__(self, private_key, provider):

        	self.web3 = Web3(HTTPProvider(provider))
        	assert web3.isConnected()
        	self.key = private_key
        	self.address = ethereum.utils.privtoaddr(private_key)
		assert web3.isAddress(self.address)

    def get_balance(self):
        """
        Return the balance of the address

        """
        assert web3.isConnected()
        balance = web3.eth.getBalance(self.address) 

        return balance


    def pay(self, addressToSend, amount, fee=get_network_fee(),number_gas=NB_GAS_FOR_TRANSACTION): 
    	"""
    	Function to send ether to an address, you can choose the fees
    	
    	"""
	assert web3.isConnected()
	nonceAddress=web3.eth.getTransactionCount(self.address)
	assert web3.isAddress(addressToSend)
	
	amount_In_Wei = amount*ETHER_TO_WEI
	fee_In_Wei = fee*10**9 # 1 Gwei = 1 billion wei
	
	tx = Transaction(
	nonce = nonceAddress,
	gasprice = fee_In_Wei, 
	startgas = number_gas,
	to = addressToSend,
	value = amount_In_Wei,
	data = b'', # no need of additional data
	)
	tx.sign(self.key)
	raw_tx = rlp.encode(tx)
	raw_tx_hex = web3.toHex(raw_tx)
	txHash = web3.eth.sendRawTransaction(raw_tx_hex)
	
	return txHash


