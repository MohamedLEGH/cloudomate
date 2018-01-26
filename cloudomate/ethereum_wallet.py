#! /usr/bin/env python3
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
from ethereum.utils import privtoaddr,checksum_encode,sha3,encode_hex

NB_GAS_FOR_TRANSACTION = 21000

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
    gwei_price = float(response['safe_price_in_gwei'])
    return gwei_price


class Wallet:
    """
    Wallet implements an adapter to the wallet handler.
    Currently Wallet only supports electrum wallets without passwords for automated operation.
    Wallets with passwords may still be used, but passwords will have to be entered manually.
    """
    def create_private_key():
        """
        To create a private key, may not be secure
        """
        
        private_key = encode_hex(sha3(os.urandom(4096)))
        return private_key

    def get_Infura_node():
        """
        To get an access to the infura service
        """    
        return "https://ropsten.infura.io/FFxYa0JaUoDljkoTWMQG"

    def __init__(self, private_key=create_private_key(), Ethprovider=get_Infura_node()):
        """
	
	You need to provide a private key (to sign transaction) and a node provider (to allow send of transactions on the network.
	
	Example
	
	## Main Network ##
	
	web3 = Web3(HTTPProvider('localhost:8545')) # need a local node, light node don't work, and I don't have enough space for full node
	web3 = Web3(HTTPProvider('https://api.myetherapi.com/eth')) # don't work, 403 error
	
	web3 = Web3(HTTPProvider('https://mainnet.infura.io/YOUR_API_KEY'))
	
	## Ropsten ##
	
	web3 = Web3(HTTPProvider('https://api.myetherapi.com/rop')) # for Ropsten network, don't work
	
	web3 = Web3(HTTPProvider('https://ropsten.infura.io/YOUR_API_KEY')) 
	
	"""
        self.web3 = Web3(HTTPProvider(Ethprovider))
        assert self.web3.isConnected()
        self.key = private_key
        raw = privtoaddr(private_key)
        self.address = checksum_encode(raw)
        assert self.web3.isAddress(self.address)
        
    def get_balance(self):
        """
        Return the balance of the address

        """
        assert self.web3.isConnected()
        balance_In_Wei = self.web3.eth.getBalance(self.address) 
        balance = self.web3.fromWei(balance_In_Wei, 'ether')
        return balance


    def pay(self, addressToSend, amount, fee=get_network_fee(),number_gas=NB_GAS_FOR_TRANSACTION): 
        """
        Function to send ether to an address, you can choose the fees
        
        """
        assert self.web3.isConnected()
        nonceAddress = self.web3.eth.getTransactionCount(self.address)
        assert self.web3.isAddress(addressToSend)
	
        amount_In_Wei = self.web3.toWei(amount, 'ether') 
        fee_In_Wei = self.web3.toWei(fee, 'gwei') # 1 Gwei = 1 billion wei
	
        if(self.web3.eth.getBalance(self.address) >= amount_In_Wei + fee_In_Wei):
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
            raw_tx_hex = self.web3.toHex(raw_tx)
            txHash = self.web3.eth.sendRawTransaction(raw_tx_hex)
            return txHash
        else:
            print("No enough ether on your account")

def main():
	user_private_key = input("Please enter private key:")
	user_Eth_provider = input("Please enter an url to an Eth provider:")
	
	MyWallet = Wallet(user_private_key,user_Eth_provider)
	
	print(MyWallet.get_balance())
	
	address_ToSend_eth = input("Please enter an address to send eth :")
	
	user_amount = float(input("Please provide an amount to send (in ether) : "))
	
	txHash = MyWallet.pay(address_ToSend_eth,user_amount)
	print("Your txHash is :" + str(txHash))
	
if __name__ == "__main__":
	main()
