import os
import secrets
import struct

from cryptography.hazmat.primitives.ciphers import algorithms
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.ciphers.aead import AESOCB3

nonce = os.urandom(8)
counter = 0
full_nonce = struct.pack("<Q", counter) + nonce
algorithm = algorithms.ChaCha20(key, full_nonce)
cipher = Cipher(algorithm, mode=None)
encryptor = cipher.encryptor()

# ruleid: cryptography-insecure-random
nonce = b"This-is-clearly-not-random"
counter = 0
full_nonce = struct.pack("<Q", counter) + nonce
algorithm = algorithms.ChaCha20(key, full_nonce)
cipher = Cipher(algorithm, mode=None)
encryptor = cipher.encryptor()

# ruleid: cryptography-insecure-random
nonce = os.random(8)
counter = 0
full_nonce = struct.pack("<Q", counter) + nonce
algorithm = algorithms.ChaCha20(key, full_nonce)
cipher = Cipher(algorithm, mode=None)
encryptor = cipher.encryptor()
