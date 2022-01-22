import codecs
import json
import os
import random

import flask
from flask import Response
from flask import jsonify
from flask import request

import pysrc.Blockchain as B
import pysrc.Ethereum as eth
import pysrc.SmartNFT as nft
import pysrc.Transaction as T

app = flask.Flask(__name__)
ownerAddresses = []
userAddresses = []
deviceAddresses = []
blockchain = B.Blockchain()

nfts = []
tokenIds = 0


def makeTransactionWithNFTAndSign(smartToken, _gas, _sender, operation):
    transaction = T.Transaction(sender=_sender, recipient="SmartContract",
                                amount="0 SNFT",
                                gas="{} SNFT".format(_gas),
                                contractData={
                                    "contractOperation": operation,
                                    "nft": smartToken.__repr__()
                                })
    addrInfo = getAddressInfo(ownerAddresses, smartToken.ownerAddr)
    transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
    blockchain.put_trx_in_mempool([transaction])

    return transaction


def makeTransactionAndSign(_gas, _sender, _amount, _recipient):
    transaction = T.Transaction(sender=_sender, recipient=_recipient,
                                amount=f"{_amount} SNFT",
                                gas=f"{_gas} SNFT",
                                contractData=None)
    addrInfo = getAddressInfo(ownerAddresses, _sender)
    transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
    blockchain.put_trx_in_mempool([transaction])

    return transaction


def computeSignature(transaction, signing_key):
    """Computes a signature of a transaction hash.

    :param transaction: Transaction object
    :param signing_key: private key with which the transaction is going to be signed
    :return: string hex representation of signature
    """
    return codecs.encode(
        eth.signTransaction(
            signing_key,
            bytes(transaction.transaction_hash, 'utf-8'))
        , 'hex')


# TODO: Transactions objects are not being stored anywhere, thus I cannot check with original Transaction object.
#       There might be a possibility to save Transaction objects to mempool/blockchain itself, but it needs
#       a refactor of Blockchain class
# def verifySignature(transaction, verifying_key, signatureToVerify):
#     return transaction.verifyTransaction()

def getAddressInfo(listOfAddresses, address):
    for obj in listOfAddresses:
        if obj['wallet_address'] == address:
            return obj


def checkExistenceOfAnAddress(listOfAddresses, address):
    for obj in listOfAddresses:
        if obj['wallet_address'] == address:
            return True
    return False


def getNFTFromMemory(nftTokenId):
    for nft in nfts:
        if nft.tokenId == nftTokenId:
            return nft


def checkExistenceOfNFT(nftTokenId):
    for nft in nfts:
        if nft.tokenId == nftTokenId:
            return True
    return False


def checkParams(request_params, *required_parameters):
    missing_params = []
    for key in required_parameters:
        if key not in request_params:
            missing_params.append(key)
    if len(missing_params) > 0:
        return [False, "{} missing in the parameter list.".format(missing_params)]
    return [True]


@app.route('/')
@app.route('/index')
def print_index():
    return open('./index.html', 'r').read()


@app.route('/api/setBlockchainDifficulty', methods=['PUT'])
def setDifficulty():
    correctParameters = checkParams(request.args, "difficulty")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    difficulty = request.args.get('difficulty', default=0, type=int)
    blockchain.set_difficulty(difficulty)
    return jsonify(success=True, message="Blockchain difficulty set to {}.".format(blockchain.difficulty))


@app.route('/api/getUserAddresses', methods=['GET'])
def getExistingUserAddresses():
    serializedUserAddr = []
    for wallet in userAddresses:
        serializedUserAddr.append(
            {
                "wallet_address": wallet['wallet_address'],
                # "private_key": codecs.encode(wallet['private_key_b'], 'hex').decode('utf-8'),
                # "public_key": codecs.encode(wallet['public_key'].to_string(), 'hex').decode('utf-8')
            })
    return jsonify(serializedUserAddr)


@app.route('/api/getOwnerAddresses', methods=['GET'])
def getExistingOwnerAddresses():
    serializedOwnerAddr = []
    for wallet in ownerAddresses:
        serializedOwnerAddr.append(
            {
                "wallet_address": wallet['wallet_address'],
                # "private_key": codecs.encode(wallet['private_key_b'], 'hex').decode('utf-8'),
                # "public_key": codecs.encode(wallet['public_key'].to_string(), 'hex').decode('utf-8')
            })
    return jsonify(serializedOwnerAddr)


@app.route('/api/createNewUserAddresses', methods=['POST'])
def createNewUserAddresses():
    correctParameters = checkParams(request.args, "count")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    countOfAddresses = request.args.get('count', default=0, type=int)
    for _ in range(0, countOfAddresses):
        userAddresses.append(eth.generateKeysAndAddress())
    return jsonify(success=True, message="{} user addresses successfully created.".format(countOfAddresses))


@app.route('/api/createNewOwnerAddresses', methods=['POST'])
def createNewOwnerAddresses():
    correctParameters = checkParams(request.args, "count")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    countOfAddresses = request.args.get('count', default=0, type=int)
    for _ in range(0, countOfAddresses):
        ownerAddresses.append(eth.generateKeysAndAddress())
    return jsonify(success=True, message="{} owner addresses successfully created.".format(countOfAddresses))


@app.route('/api/getBlockchain', methods=['GET'])
def getBlockchain():
    return jsonify(success=True, blocks=blockchain.get_blocks())


@app.route('/api/computeNewBlock', methods=['PUT'])
def computeNewBlock():
    blockchain.new_block()
    return jsonify(success=True,
                   message="A new block with index {} was created.".format(blockchain.chain[-1]['index']),
                   computedBlock=blockchain.chain[-1])


@app.route('/api/createToken', methods=['POST'])
def createToken():
    """ Creates an NFT device. Stores it in memory for further processing and writes it in a transaction to be
        written into the blockchain.

    :return: Flask Response in case of a failure. JSON object in case of success.
    """
    # Check params of request
    global tokenIds
    correctParameters = checkParams(request.args, "timeout", "ownerAddress")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    timeout = request.args.get('timeout', default=0, type=int)
    deviceOwnerAddress = request.args.get('ownerAddress', default="0", type=str)

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, deviceOwnerAddress):
        return Response(json.dumps({"success": False, "message": f"Address {deviceOwnerAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    # Create NFT
    deviceAddresses.append(eth.generateKeysAndAddress())
    smartToken = nft.SmartNFT(initialOwnerAddress=deviceOwnerAddress,
                              deviceAddress=deviceAddresses[-1]['wallet_address'], tokenId=tokenIds, timeout=timeout)
    tokenIds += 1
    nfts.append(smartToken)

    # Write NFT into a transaction as contractData
    transaction = makeTransactionWithNFTAndSign(smartToken, random.randint(2500, 10000), smartToken.ownerAddr, "CreateToken")
    return jsonify(success=True,
                   message="Device with address {} and tokenID {} successfully created. Written into transaction "
                           "with transaction hash {}."
                   .format(smartToken.deviceAddr, smartToken.tokenId, transaction.transaction_hash),
                   deviceAddress=smartToken.deviceAddr,
                   transaction=transaction.__repr__(),
                   transactionHash=transaction.transaction_hash)


@app.route('/api/getAllTokens', methods=['GET'])
def getTokens():
    nfts_str = []
    for snft in nfts:
        nfts_str.append(snft.__repr__())
    return jsonify(success=True, nfts=nfts_str)


@app.route('/api/transferNFTOwner', methods=['PUT'])
def transferNFTOwner():
    """Function for NFT Owner transfer.

    :param newOwnerAddress: address of a new NFT owner
    :param ownerAddress: address of the old NFT owner
    :param tokenId: tokenId of NFT in question
    :return: Response object with appropriate response
    """
    # Check params of request
    correctParameters = checkParams(request.args, "newOwnerAddress", "ownerAddress", "tokenId")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    newDeviceOwnerAddress = request.args.get('newOwnerAddress', default="0", type=str)
    deviceOwnerAddress = request.args.get('ownerAddress', default="0", type=str)
    tokenIdToTransfer = request.args.get('tokenId', default=-1, type=int)

    # Check existence of an NFT on input
    if not checkExistenceOfNFT(tokenIdToTransfer):
        return Response(
            json.dumps({"success": False, "message": f"NFT with tokenId {tokenIdToTransfer} does not exist"}),
            status=404,
            content_type="application/json")

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, deviceOwnerAddress):
        return Response(json.dumps({"success": False, "message": f"Address {deviceOwnerAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, newDeviceOwnerAddress):
        return Response(json.dumps({"success": False, "message": f"Address {newDeviceOwnerAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    nft_tmp = getNFTFromMemory(tokenIdToTransfer)
    result = nft_tmp.transferFrom(deviceOwnerAddress, newDeviceOwnerAddress)
    print(result)
    if not result[0]:
        return Response(
            json.dumps({"success": False, "message": result[1]}),
            status=400,
            content_type="application/json")
    else:
        # Write NFT into a transaction as contractData
        transaction = T.Transaction(sender=deviceOwnerAddress, recipient="SmartContract",
                                    amount="0 SNFT",
                                    gas="{} SNFT".format(result[2]),
                                    contractData={
                                        "contractOperation": "TransferOwner",
                                        "nft": nft_tmp.__repr__()
                                    })
        addrInfo = getAddressInfo(ownerAddresses, nft_tmp.ownerAddr)
        transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
        blockchain.put_trx_in_mempool([transaction])
        return Response(
            json.dumps({"success": True,
                        "message": f"Token with tokenId {tokenIdToTransfer} transfered to a new owner {newDeviceOwnerAddress}. Change written into a transaction {transaction.transaction_hash}",
                        "transaction": transaction.__repr__()}),
            status=200,
            content_type="application/json")


@app.route('/api/setNFTUser', methods=['PUT'])
def setNFTUser():
    # Check params of request
    correctParameters = checkParams(request.args, "newUserAddress", "ownerAddress", "tokenId", 'ignoreUserCheck')
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    newDeviceUserAddress = request.args.get('newUserAddress', default="0", type=str)
    deviceOwnerAddress = request.args.get('ownerAddress', default="0", type=str)
    tokenIdToTransfer = request.args.get('tokenId', default=-1, type=int)
    ignoreUserAddressCheck = request.args.get('ignoreUserCheck', default=False, type=bool)

    # Check existence of an NFT on input
    if not checkExistenceOfNFT(tokenIdToTransfer):
        return Response(
            json.dumps({"success": False, "message": f"NFT with tokenId {tokenIdToTransfer} does not exist"}),
            status=404,
            content_type="application/json")

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, deviceOwnerAddress):
        return Response(json.dumps({"success": False, "message": f"Address {deviceOwnerAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    # Check existence of an address on input
    if not ignoreUserAddressCheck and not checkExistenceOfAnAddress(userAddresses, newDeviceUserAddress):
        return Response(json.dumps({"success": False, "message": f"Address {newDeviceUserAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    nft_tmp = getNFTFromMemory(tokenIdToTransfer)
    result = nft_tmp.setUser(deviceOwnerAddress, newDeviceUserAddress)
    if not result[0]:
        return Response(
            json.dumps({"success": False, "message": result[1]}),
            status=400,
            content_type="application/json")
    else:
        # Write NFT into a transaction as contractData
        transaction = T.Transaction(sender=deviceOwnerAddress, recipient="SmartContract",
                                    amount="0 SNFT",
                                    gas="{} SNFT".format(result[2]),
                                    contractData={
                                        "contractOperation": "SetNFTUser",
                                        "nft": nft_tmp.__repr__()
                                    })
        addrInfo = getAddressInfo(ownerAddresses, nft_tmp.ownerAddr)
        transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
        blockchain.put_trx_in_mempool([transaction])
        return Response(
            json.dumps({"success": True,
                        "message": f"{result[1]} Change written into a transaction {transaction.transaction_hash}",
                        "transaction": transaction.__repr__()}),
            status=200,
            content_type="application/json")


@app.route('/api/engageNFTUser', methods=['PUT'])
def engageNFTUser():
    # Check params of request
    correctParameters = checkParams(request.args, "userAddressEngage", "tokenId", "ignoreUserCheck")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    deviceUserAddress = request.args.get('userAddressEngage', default="0", type=str)
    tokenIdToEngage = request.args.get('tokenId', default=-1, type=int)
    ignoreUserCheck = request.args.get('ignoreUserCheck', default=False, type=bool)

    # Check existence of an NFT on input
    if not checkExistenceOfNFT(tokenIdToEngage):
        return Response(
            json.dumps({"success": False, "message": f"NFT with tokenId {tokenIdToEngage} does not exist"}),
            status=404,
            content_type="application/json")

    # Check existence of an address on input
    if not ignoreUserCheck and not checkExistenceOfAnAddress(userAddresses, deviceUserAddress):
        return Response(json.dumps({"success": False, "message": f"Address {deviceUserAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    nft_tmp = getNFTFromMemory(tokenIdToEngage)
    result = nft_tmp.userEngagement(deviceUserAddress, tokenIdToEngage)
    if not result[0]:
        return Response(
            json.dumps({"success": False, "message": result[1]}),
            status=400,
            content_type="application/json")
    else:
        # Write NFT into a transaction as contractData
        transaction = T.Transaction(sender=deviceUserAddress, recipient="SmartContract",
                                    amount="0 SNFT",
                                    gas="{} SNFT".format(result[2]),
                                    contractData={
                                        "contractOperation": "EngageNFTUser",
                                        "nft": nft_tmp.__repr__()
                                    })
        addrInfo = getAddressInfo(ownerAddresses, nft_tmp.ownerAddr)
        transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
        blockchain.put_trx_in_mempool([transaction])
        return Response(
            json.dumps({"success": True,
                        "message": f"{result[1]} Change written into a transaction {transaction.transaction_hash}",
                        "transaction": transaction.__repr__()}),
            status=200,
            content_type="application/json")


@app.route('/api/engageNFTOwner', methods=['PUT'])
def engageNFTOwner():
    # Check params of request
    correctParameters = checkParams(request.args, "ownerAddressEngage", "tokenId")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    deviceOwnerAddress = request.args.get('ownerAddressEngage', default="0", type=str)
    tokenIdToEngage = request.args.get('tokenId', default=-1, type=int)

    # Check existence of an NFT on input
    if not checkExistenceOfNFT(tokenIdToEngage):
        return Response(
            json.dumps({"success": False, "message": f"NFT with tokenId {tokenIdToEngage} does not exist"}),
            status=404,
            content_type="application/json")

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, deviceOwnerAddress):
        return Response(json.dumps({"success": False, "message": f"Address {deviceOwnerAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    nft_tmp = getNFTFromMemory(tokenIdToEngage)
    result = nft_tmp.ownerEngagement(deviceOwnerAddress, tokenIdToEngage)
    if not result[0]:
        return Response(
            json.dumps({"success": False, "message": result[1]}),
            status=400,
            content_type="application/json")
    else:
        # Write NFT into a transaction as contractData
        transaction = T.Transaction(sender=deviceOwnerAddress, recipient="SmartContract",
                                    amount="0 SNFT",
                                    gas="{} SNFT".format(result[2]),
                                    contractData={
                                        "contractOperation": "EngageNFTOwner",
                                        "nft": nft_tmp.__repr__()
                                    })
        addrInfo = getAddressInfo(ownerAddresses, nft_tmp.ownerAddr)
        transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
        blockchain.put_trx_in_mempool([transaction])
        return Response(
            json.dumps({"success": True,
                        "message": f"{result[1]} Change written into a transaction {transaction.transaction_hash}",
                        "transaction": transaction.__repr__()}),
            status=200,
            content_type="application/json")


@app.route('/api/postTransaction', methods=['POST'])
def postTransaction():
    # Check params of request
    correctParameters = checkParams(request.args, "sender", "recipient", "amount")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    senderAddress = request.args.get('sender', default="0", type=str)
    recipientAddress = request.args.get('recipient', default="0", type=str)
    trxAmount = request.args.get('amount', default=1, type=int)

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(ownerAddresses, senderAddress):
        return Response(json.dumps({"success": False, "message": f"Address {senderAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    # Check existence of an address on input
    if not checkExistenceOfAnAddress(userAddresses, recipientAddress):
        return Response(json.dumps({"success": False, "message": f"Address {recipientAddress} does not exist"}),
                        status=404,
                        content_type="application/json")

    # Create a transaction and put into a block
    transaction = makeTransactionAndSign(random.randint(1000, 30000), senderAddress, trxAmount, recipientAddress)
    return Response(
        json.dumps({"success": True,
                    "message": f"Transaction with hash {transaction.transaction_hash} sent to mempool",
                    "transaction": transaction.__repr__()}),
        status=200,
        content_type="application/json")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
