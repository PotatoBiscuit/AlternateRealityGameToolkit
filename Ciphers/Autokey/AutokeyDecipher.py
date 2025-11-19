import argparse

alphabet_len = 26

parser = argparse.ArgumentParser(
    prog="AutokeyDecipher",
    description="""Decipher script for the Autokey cipher. Part of the key is built dynamically during decryption:
    the initial key is used first, then each decrypted plaintext character is appended to the key to
    decrypt subsequent characters."""
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")

parser.add_argument('secret_key',
                    type=str,
                    help="Initial key used during encryption")

args = parser.parse_args()

encrypted_message = args.encrypted_message.replace(" ", "").lower()
secret_key = args.secret_key.replace(" ", "").lower()

ascii_offset = 97
decrypted_message = ""

# Start with the initial key and build it as we decrypt
current_key = secret_key
message_len = len(encrypted_message)

for i in range(message_len):
    cipher_char_val = ord(encrypted_message[i]) - ascii_offset
    key_char_val = ord(current_key[i]) - ascii_offset

    # Decrypt: subtract the key value from the cipher value
    decrypted_char_val = (cipher_char_val - key_char_val) % alphabet_len
    decrypted_char = chr(decrypted_char_val + ascii_offset)

    decrypted_message += decrypted_char
    # Append the decrypted character to the key for the next iteration
    current_key += decrypted_char

print("Encrypted Message: " + encrypted_message)
print("Secret Key: " + secret_key)
print("Decrypted Message: " + decrypted_message)
