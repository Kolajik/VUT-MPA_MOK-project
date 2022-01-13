import random
import time
from datetime import datetime


class SmartNFT:
    states = {"WO": "Waiting for owner",
              "EO": "Engaged with owner",
              "EU": "Engaged with User",
              "WU": "Waiting for user"}

    def __init__(self, initialOwnerAddress, deviceAddress, tokenId, timeout):
        self.tokenId = tokenId
        self.state = self.states['WO']
        self.userAddr = None
        self.ownerAddr = initialOwnerAddress
        self.deviceAddr = deviceAddress
        self.timestamp = time.localtime()
        self.timeout = timeout

    def __repr__(self):
        return {
            "tokenId": self.tokenId,
            "ownerAddress": self.ownerAddr,
            "deviceAddress": self.deviceAddr,
            "userAddress": self.userAddr,
            "state": self.state,
            "timestamp": time.strftime("%d/%m/%Y, %H:%M:%S", self.timestamp),
            "timeout": self.timeout
        }

    def transferFrom(self, _from, _to):
        if _from != self.ownerAddr:
            return [False, "{} is not the token owner.".format(_from)]
        else:
            self.ownerAddr = _to
            self.state = self.states['EO']
            return [True, "Token with id {} transferred from {} owner to a new owner with address {}".format(self.tokenId, _from, self.ownerAddr), random.randint(3000, 15000)]

    def setUser(self, _owner, _user):
        if self.userAddr == _user:
            return [False, "{} is already a user.".format(_user)]
        elif self.ownerAddr != _owner:
            return [False, "{} is not the owner.".format(_owner)]
        elif self.state not in [self.states['EO'], self.states['WU']]:
            return [False, "Incorrect state of the device - {}.".format(self.state)]
        else:
            self.userAddr = _user
            if self.userAddr == self.ownerAddr:
                self.state = self.states['EU']
            else:
                self.state = self.states['WU']
            return [True, "Token with id {} has now user with address {}.".format(self.tokenId, self.userAddr), random.randint(3000, 10000)]

    def userEngagement(self, _user, _tokenId):
        if self.userAddr != _user or self.tokenId != _tokenId:
            return [False, "{} is not the user of token {}.".format(_user, self.tokenId)]
        elif self.state != self.states['WU']:
            return [False, "Incorrect state of the device - {}.".format(self.state)]
        else:
            self.state = self.states['EU']
            return [True, "State of the token {} set to \"{}\".".format(self.tokenId, self.state), random.randint(100, 3000)]

    def ownerEngagement(self, _owner, _tokenId):
        if self.ownerAddr != _owner or self.tokenId != _tokenId:
            return [False, "{} is not the owner of token {}.".format(_owner, self.tokenId)]
        elif self.state != self.states['WO']:
            return [False, "Incorrect state of the device - {}.".format(self.state)]
        else:
            self.state = self.states['EO']
            return [True, "State of the token {} set to \"{}\".".format(self.tokenId, self.state), random.randint(10, 3000)]

    def setTimeout(self, _owner, timeout, _tokenId):
        if self.ownerAddr != _owner or self.tokenId != _tokenId:
            return [False, "{} is not the owner of token {}.".format(_owner, self.tokenId)]
        else:
            self.timeout = timeout
            return [True, "Timeout of the token {} set to {}.".format(self.tokenId, self.timeout), random.randint(100, 300)]

    def checkTimeout(self, blockTimestamp):
        if (time.mktime(self.timestamp.__getitem__(0)) + self.timeout) >= time.mktime(blockTimestamp.__getitem__(0)):
            return True
        else:
            return False