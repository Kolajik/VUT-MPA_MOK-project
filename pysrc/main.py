import random
import string

import Transaction as T, Blockchain as B

if __name__ == '__main__':
    blockchain = B.Blockchain()
    blockchain.set_difficulty(4)

    # Set genesis block transaction (coinbase transaction)
    genesis_trx = [T.Transaction("MINER", "Satoshi", "1500 MOK")]
    blockchain.put_trx_in_block(genesis_trx)
    blockchain.new_block()

    # Set more transactions and a new block
    trxs = [T.Transaction("Satoshi", "Mike", '5 MOK'), T.Transaction("Mike", "Satoshi", '1 MOK'),
            T.Transaction("Satoshi", "Dave", '10 MOK'), T.Transaction("Dave", "Mike", '3 MOK')]
    blockchain.put_trx_in_block(trxs)
    blockchain.new_block()

    for i in range(1, 6):
        trxs = []
        for _ in range(0, i + 3):
            sender = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
            recipient = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))
            amount = random.randint(50, 2000)
            trx = T.Transaction(sender, recipient, str(amount) + ' MOK')
            trxs.append(trx)
        blockchain.set_difficulty(diff=i)
        blockchain.put_trx_in_block(trxs)
        blockchain.new_block()

    print("Blockchain: \n{}\n".format(blockchain.chain))
    # blockchain.search_transaction('ecba2d')
