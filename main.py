import random
import string
import flask
import os

import pysrc.Transaction as T
import pysrc.Blockchain as B

app = flask.Flask(__name__)

@app.route('/')
@app.route('/index')
def print_index():
    return open('./index.html', 'r').read()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)

    # blockchain = B.Blockchain()
    # blockchain.set_difficulty(4)
    #
    # # Set genesis block transaction (coinbase transaction)
    # genesis_trx = [T.Transaction("MINER", "Satoshi", "1500 MOK")]
    # blockchain.put_trx_in_block(genesis_trx)
    # blockchain.new_block()
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
