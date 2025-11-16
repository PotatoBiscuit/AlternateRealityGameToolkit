import argparse

alphabet_len = 26

parser = argparse.ArgumentParser(
    prog="AlphabetDecipher",
    description="""Decipher script for Lewis Carroll's Alphabet Cipher from 1868. Reverses the tabula recta
    encoding by subtracting the key values instead of adding them."""
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")

parser.add_argument('secret_key',
                    type=str,
                    help="Key used to encrypt the message")

args = parser.parse_args()

encrypted_message = args.encrypted_message.replace(" ", "").lower()
secret_key = args.secret_key.replace(" ", "").lower()

secret_key_len = len(secret_key)

ascii_offset = 97
decrypted_message = ""

key_ind = 0
for character in encrypted_message:
    # To decrypt, we subtract the key value instead of adding it
    decrypted_message += chr((((ord(character) - ascii_offset) - (ord(secret_key[key_ind]) - ascii_offset)) % alphabet_len) + ascii_offset)
    key_ind = (key_ind + 1) % secret_key_len

print("Encrypted Message: " + encrypted_message)
print("Secret Key: " + secret_key)
print("Decrypted Message: " + decrypted_message)
