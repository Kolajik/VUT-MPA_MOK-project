import codecs
import hashlib
import secrets

import ecdsa
from Crypto.Hash import keccak


def generateKeysAndAddress():
    """Generate public, private keys and corresponding ETH address.

    :return: dictionary with parameters of an ETH address
    """

    # ECDSA private key
    priv_key = secrets.token_hex(32)
    priv_key_byte = codecs.decode(priv_key, 'hex')
    # print("private key = {}\nsigning key bytes = {}".format(priv_key, codecs.encode(priv_key_byte, 'hex')))

    # ECDSA Public key
    pub_key = ecdsa.SigningKey.from_string(priv_key_byte, curve=ecdsa.SECP256k1,
                                           hashfunc=hashlib.sha3_256).verifying_key
    # pub_key_bytes = codecs.encode(pub_key.to_string(), 'hex')
    # print("public key = {}\nverifying key bytes = {}".format(pub_key.to_string(), pub_key_bytes))

    # ETH wallet address
    wallet_address = keccak.new(digest_bits=256)
    wallet_address.update(pub_key.to_string())
    # print("{}\n0x{}".format(wallet_address.hexdigest(), wallet_address.hexdigest()[24:]))

    return {
        "wallet_address": "0x" + wallet_address.hexdigest()[24:],
        "private_key_b": priv_key_byte,
        "public_key": pub_key
    }


def signTransaction(signing_key_bytes, transaction_bytes):
    """Signs a transaction on input with the signing key.

    :param signing_key_bytes: private key with which the transaction is going to be signed
    :param transaction_bytes: transaction which is going to be signed
    :return: ECDSA signature hash
    """
    return ecdsa.SigningKey.from_string(signing_key_bytes, curve=ecdsa.SECP256k1, hashfunc=hashlib.sha3_256).sign(
        transaction_bytes)


def verifyTransaction(verifying_key, transaction_bytes, transaction_signature_bytes):
    """Verifies if the transaction signature is valid.

    :param verifying_key: ecdsa object with verifying key
    :param transaction_bytes: original transaction data
    :param transaction_signature_bytes: signature hash
    :return: boolean result of the verify process
    """
    return verifying_key.verify(transaction_signature_bytes, transaction_bytes)
