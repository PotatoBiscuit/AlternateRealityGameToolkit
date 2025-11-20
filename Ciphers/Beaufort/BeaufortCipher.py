#!/usr/bin/env python3
"""
Beaufort Cipher - A polyalphabetic substitution cipher related to the Vigenère cipher.

Created by Sir Francis Beaufort in 1857, this cipher is similar to the Vigenère cipher but uses
subtraction instead of addition. The formula is: C = (K - P) mod 26, where C is the ciphertext,
K is the key, and P is the plaintext. The cipher is reciprocal (involutory), meaning encryption
and decryption use the same operation.
"""

import argparse

alphabet_len = 26

parser = argparse.ArgumentParser(
    prog="BeaufortCipher",
    description="""The Beaufort cipher is a polyalphabetic substitution cipher invented by Sir Francis Beaufort.
    Unlike the Vigenère cipher which adds key to plaintext, the Beaufort cipher subtracts plaintext from key:
    C = (K - P) mod 26. This cipher is involutory, meaning the same operation encrypts and decrypts."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('secret_key',
                    type=str,
                    help="Key used for encryption (will repeat if shorter than message)")

args = parser.parse_args()

secret_message = args.secret_message.replace(" ", "").lower()
secret_key = args.secret_key.replace(" ", "").lower()

ascii_offset = 97
encrypted_message = ""

# Repeat the key to match the message length
key_len = len(secret_key)
message_len = len(secret_message)

for i in range(message_len):
    message_char_val = ord(secret_message[i]) - ascii_offset
    key_char_val = ord(secret_key[i % key_len]) - ascii_offset

    # Beaufort cipher formula: C = (K - P) mod 26
    encrypted_char = chr(((51 - key_char_val - message_char_val) % alphabet_len) + ascii_offset)
    encrypted_message += encrypted_char

print("Original Message: " + secret_message)
print("Secret Key: " + secret_key)
print("Encrypted Message: " + encrypted_message)
