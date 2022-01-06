import time


class SmartNFT:
    states = {"WO": "Waiting for owner",
              "EO": "Engaged with owner",
              "EU": "Engaged with User",
              "WU": "Waiting for user"}

    def __init__(self, deviceAddress, tokenId):
        self.tokenId = tokenId
        self.state = self.states['WO']
        self.userAddr = None
        self.ownerAddr = None
        self.deviceAddr = deviceAddress
        self.timestamp = time.strftime("%m/%d/%Y, %H:%M:%S")

    def __repr__(self):
        return {
            "tokenId": self.tokenId,
            "ownerAddress": self.ownerAddr,
            "deviceAddress": self.deviceAddr,
            "state": self.state,
            "timestamp": self.timestamp
        }

    def transferFrom(self, _from, _to):
        if _from != self.ownerAddr:
            return [False, "{} is not the token owner.".format(_from)]
        else:
            self.ownerAddr = _to
            self.state = self.states['EO']
            return [True, "Token with id {} transferred from {} owner to a new owner with address {}".format(self.tokenId, _from, self.ownerAddr)]

    def setUser(self, _user):
        if self.userAddr == _user:
            return [False, "{} is already a user.".format(_user)]
        elif self.state != self.states['EO'] or self.state != self.states['WU']:
            return [False, "Incorrect state of the device - {}.".format(self.state)]
        else:
            self.userAddr = _user
            self.state = self.states['EO']
            return [True, "Token with id {} has now user with address {}.".format(self.tokenId, self.userAddr)]