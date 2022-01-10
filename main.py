import random
import string
import time

import flask
from flask import jsonify
from flask import request
from flask import Response
import os
import codecs
import json

import pysrc.Transaction as T
import pysrc.Blockchain as B
import pysrc.Ethereum as eth
import pysrc.SmartNFT as nft

app = flask.Flask(__name__)
ownerAddresses = []
userAddresses = []
deviceAddresses = []
blockchain = B.Blockchain()

nfts = []
tokenIds = 0


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


@app.route('/api/createNewUserAddresses/', methods=['POST'])
def createNewUserAddresses():
    correctParameters = checkParams(request.args, "count")
    if not correctParameters[0]:
        return Response(json.dumps({"success": False, "message": correctParameters[1]}), status=400,
                        content_type="application/json")
    countOfAddresses = request.args.get('count', default=0, type=int)
    for _ in range(0, countOfAddresses):
        userAddresses.append(eth.generateKeysAndAddress())
    return jsonify(success=True, message="{} user addresses successfully created.".format(countOfAddresses))


@app.route('/api/createNewOwnerAddresses/', methods=['POST'])
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
    return jsonify(blockchain.chain)


@app.route('/api/createToken/', methods=['POST'])
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
    transaction = T.Transaction(sender=smartToken.ownerAddr, recipient="SmartContract",
                                amount="0 SNFT",
                                gas="{} SNFT".format(random.randint(2500, 10000)),
                                contractData={
                                    "contractOperation": "CreateToken",
                                    "nft": smartToken.__repr__()
                                })
    addrInfo = getAddressInfo(ownerAddresses, smartToken.ownerAddr)
    transaction.setSignature(computeSignature(transaction, addrInfo['private_key_b']))
    blockchain.put_trx_in_mempool([transaction])
    return jsonify(success=True,
                   message="Device with address {} and tokenID {} successfully created. Written into transaction "
                           "with transaction hash {}."
                   .format(smartToken.deviceAddr, smartToken.tokenId, transaction.transaction_hash),
                   deviceAddress=smartToken.deviceAddr,
                   transactionHash=transaction.transaction_hash)


@app.route('/api/computeNewBlock', methods=['PUT'])
def computeNewBlock():
    blockchain.new_block()
    return jsonify(success=True,
                   message="A new block with index {} was created.".format(blockchain.chain[-1]['index']),
                   computedBlock=blockchain.chain[-1])


@app.route('/api/getAllTokens', methods=['GET'])
def getTokens():
    nfts_str = []
    for snft in nfts:
        nfts_str.append(snft.__repr__())
    return jsonify(success=True, nfts=nfts_str)


@app.route('/api/transferNFTOwner', methods=['PUT'])
def transferNFTOwner():
    """

    :return:
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

    nft_tmp = getNFTFromMemory(tokenIdToTransfer)
    result = nft_tmp.transferFrom(deviceOwnerAddress, newDeviceOwnerAddress)
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
                        "message": f"Token with tokenId {tokenIdToTransfer} transfered to a new owner {newDeviceOwnerAddress}. Change written into a transaction {transaction.transaction_hash}"}),
            status=200,
            content_type="application/json")


if __name__ == '__main__':
    # userAddresses.append(eth.generateKeysAndAddress())
    # userAddresses.append(eth.generateKeysAndAddress())
    # # Set genesis block transaction (coinbase transaction)
    # genesis_trx = [
    #     T.Transaction(userAddresses[0]['wallet_address'], userAddresses[1]['wallet_address'], "1500 SNFT",
    #                   random.randint(100, 5000), None)
    # ]
    # # Signing transaction
    # genesis_trx[0].signature = computeSignature(genesis_trx[0], userAddresses[0]['private_key_b'])
    #
    # # NFTs
    # deviceAddresses.append(eth.generateKeysAndAddress())
    # ownerAddresses.append(eth.generateKeysAndAddress())
    # nft0 = nft.SmartNFT(initialOwnerAddress=ownerAddresses[0]['wallet_address'],
    #                     deviceAddress=deviceAddresses[0]['wallet_address'], tokenId=999, timeout=1500)
    # result = nft0.transferFrom(None, ownerAddresses[0]['wallet_address'])
    # # print(time.mktime(nft0.timestamp.__getitem__(0)))
    # genesis_trx[0].contractData = nft0.__repr__()
    # # print(genesis_trx[0].__repr__()['contractData'])
    #
    # # Blockchain
    # blockchain.set_difficulty(4)
    # blockchain.put_trx_in_mempool(genesis_trx)
    # blockchain.new_block()
    #
    # # print(blockchain.chain)
    #
    # # Verifying transaction
    # address = userAddresses[0]['public_key']
    # trx_b = bytes(genesis_trx[0].transaction_hash, 'utf-8')
    # signature = codecs.decode(bytes(genesis_trx[0].signature), 'hex')
    # # print(eth.verifyTransaction(address, trx_b, signature))

    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

    # blockchain = B.Blockchain()
    #
    #
    # # Set more transactions and a new block
    # trxs = [T.Transaction("Satoshi", "Mike", '5 MOK'), T.Transaction("Mike", "Satoshi", '1 MOK'),
    #         T.Transaction("Satoshi", "Dave", '10 MOK'), T.Transaction("Dave", "Mike", '3 MOK')]
    # blockchain.put_trx_in_block(trxs)
    # blockchain.new_block()
    #
    # for i in range(1, 6):
    #     trxs = []
    #     for _ in range(0, i + 3):
    #         sender = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
    #         recipient = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
    #         amount = random.randint(50, 2000)
    #         trx = T.Transaction(sender, recipient, str(amount) + ' MOK')
    #         trxs.append(trx)
    #     blockchain.set_difficulty(diff=i)
    #     blockchain.put_trx_in_block(trxs)
    #     blockchain.new_block()
    #
    # print("Blockchain: \n{}\n".format(blockchain.chain))
    # # blockchain.search_transaction('ecba2d')
