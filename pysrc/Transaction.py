import codecs
import hashlib
import time
import pysrc.Ethereum
import json


class Transaction:

    def __init__(self, sender, recipient, amount):
        self.sender = sender.encode('utf-8')
        self.recipient = recipient.encode('utf-8')
        self.amount = amount
        self.timestamp = time.strftime("%m/%d/%Y, %H:%M:%S")
        concat_info = sender + recipient + str(amount) + self.timestamp
        self.transaction_hash = str(hashlib.sha3_256(concat_info.encode('utf-8')).hexdigest())
        # transaction hash is signed
        self.signature = None

    def __repr__(self):
        return {
            "signature": self.signature.decode('utf-8'),
            "sender": self.sender.decode('utf-8'),
            "recipient": self.recipient.decode('utf-8'),
            "amount": self.amount,
            "transaction_hash": self.transaction_hash,
            "timestamp": self.timestamp
        }