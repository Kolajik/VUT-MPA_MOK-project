import hashlib
import time


class Transaction:

    def __init__(self, sender, recipient, amount):
        self.sender = sender.encode('utf-8')
        self.recipient = recipient.encode('utf-8')
        self.amount = amount
        concat_info = sender + recipient + str(amount)
        self.transaction_hash = str(hashlib.sha3_256(concat_info.encode('utf-8')).hexdigest())[:6]
        self.timestamp = time.strftime("%m/%d/%Y, %H:%M:%S")

    def __repr__(self):
        return str({
            "sender": self.sender,
            "recipient": self.recipient,
            "amount": self.amount,
            "transaction_hash": self.transaction_hash,
            "timestamp": self.timestamp
        })
