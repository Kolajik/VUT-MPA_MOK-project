import random
import string
import flask
from flask import jsonify
import os
import codecs
import json

import pysrc.Transaction as T
import pysrc.Blockchain as B
import pysrc.Ethereum as eth

app = flask.Flask(__name__)
userAddresses = []
deviceAddresses = []
blockchain = B.Blockchain()
nfts = []


def signTransaction(transaction, signing_key):
    pass


@app.route('/')
@app.route('/index')
def print_index():
    return open('./index.html', 'r').read()


@app.route('/api/getETHAddress', methods=['GET'])
def getExistingAddresses():
    serialized = []
    for wallet in userAddresses:
        serialized.append(
            {
                "wallet_address": wallet['wallet_address'],
                "private_key": codecs.encode(wallet['private_key_b'], 'hex').decode('utf-8'),
                "public_key": codecs.encode(wallet['public_key'].to_string(), 'hex').decode('utf-8')
            })
    return jsonify(serialized)


@app.route('/api/createNewUserAddresses/<int:countOfAddresses>', methods=['POST'])
def createNewUserAddresses(countOfAddresses):
    for _ in range(0, countOfAddresses):
        userAddresses.append(eth.generateKeysAndAddress())
    return jsonify(success=True, message="{} user addresses successfully created.".format(countOfAddresses))


@app.route('/api/createNewDeviceAddresses/<int:countOfAddresses>', methods=['POST'])
def createNewDeviceAddresses(countOfAddresses):
    for _ in range(0, countOfAddresses):
        deviceAddresses.append(eth.generateKeysAndAddress())
    return jsonify(success=True, message="{} device addresses successfully created.".format(countOfAddresses))


@app.route('/api/getBlockchain', methods=['GET'])
def getBlockchain():
    return jsonify(blockchain.chain)


if __name__ == '__main__':
    blockchain.set_difficulty(4)
    userAddresses.append(eth.generateKeysAndAddress())
    userAddresses.append(eth.generateKeysAndAddress())
    # Set genesis block transaction (coinbase transaction)
    genesis_trx = [T.Transaction(userAddresses[0]['wallet_address'], userAddresses[1]['wallet_address'], "1500 SNFT", None)]
    # Signing transaction
    genesis_trx[0].signature = codecs.encode(
        eth.signTransaction(userAddresses[0]['private_key_b'], bytes(genesis_trx[0].transaction_hash, 'utf-8')), 'hex')

    blockchain.put_trx_in_block(genesis_trx)
    blockchain.new_block()

    print(blockchain.chain)

    # Verifying transaction
    address = userAddresses[0]['public_key']
    trx_b = bytes(genesis_trx[0].transaction_hash, 'utf-8')
    signature = codecs.decode(bytes(genesis_trx[0].signature), 'hex')
    print(eth.verifyTransaction(address, trx_b, signature))

    # port = int(os.environ.get('PORT', 8000))
    # app.run(host='0.0.0.0', port=port, debug=False)

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
