import Transaction
import hashlib
import time
import json


class Blockchain:

    def __init__(self):
        self.counter = -1
        self.difficulty = 0
        self.chain = []
        self.mempool = []

    def new_block(self):
        self.counter += 1
        time_now = time.strftime("%m/%d/%Y, %H:%M:%S")

        if len(self.chain) != 0:
            previous_hash = self.chain[-1]['block_hash']
        else:
            previous_hash = None

        hash_input = [time_now, previous_hash, str(self.mempool).encode('utf-8')]
        nonce, block_hash = self.proof_of_work(hash_input)

        block = {
            "index": self.counter,
            "timestamp": time_now,
            "difficulty": self.difficulty,
            "transactions": self.mempool,
            "transactions_hash": hashlib.sha3_256(str(self.mempool).encode('utf-8')).hexdigest(),
            "previous_hash": previous_hash,
            "block_hash": block_hash.hexdigest(),
            "nonce": nonce
        }
        self.mempool = []

        self.chain.append(block)

        # json.dump(block).encode()

    def search_transaction(self, transaction_hash):
        if len(self.chain) == 0:
            pass
        else:
            i = 0
            for block in self.chain:
                j = 0
                for transaction in block['transactions']:
                    if transaction.transaction_hash.startswith(transaction_hash):
                        print("Transaction you're looking for: {}\nIn chain with index {}".format(
                            self.chain[i]['transactions'], self.chain[i]['index']))
                        break
                    else:
                        j += 1
                i += 1

    def put_trx_in_block(self, transactions):
        # print(transactions)
        if isinstance(transactions[0], Transaction.Transaction):
            for trx in transactions:
                self.mempool.append(trx)
        else:
            print("Transaction {} not of a type Transaction.\nActual type: {}".format(transactions, type(transactions)))

    def print_blocks(self):
        print(self.chain)

    def set_difficulty(self, diff):
        self.difficulty = diff

    def proof_of_work(self, data):
        start_time = time.time()
        num_of_zeroes = "0" * self.difficulty
        nonce = 0
        current_hash = hashlib.sha3_256(str(data).encode() + str(nonce).encode())
        if self.difficulty == 0:
            return nonce, current_hash
        else:
            while not str(current_hash.hexdigest()).startswith(num_of_zeroes):
                nonce += 1
                current_hash = hashlib.sha3_256(str(data).encode() + str(nonce).encode())
        print("Proof of work output with difficulty = {}\nNonce = {}\nDigest = {}\nTime of computing block [s] = {}\n"
              .format(self.difficulty, nonce, current_hash.hexdigest(), time.time() - start_time))
        return nonce, current_hash
