import argparse

alphabet_len = 26

parser = argparse.ArgumentParser(
    prog="AutokeyCipher",
    description="""The Autokey cipher is a polyalphabetic substitution cipher invented by Blaise de Vigenère,
    and features using the plaintext message itself as part of the key. The initial key is used first, then the
    message is appended to form the complete key stream, making it more secure than repeating key ciphers."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('secret_key',
                    type=str,
                    help="Initial key used to start the encryption")

args = parser.parse_args()

secret_message = args.secret_message.replace(" ", "").lower()
secret_key = args.secret_key.replace(" ", "").lower()

ascii_offset = 97
encrypted_message = ""

# Build the full key: initial key + plaintext message
# The key is as long as the message (we only need message_len characters)
full_key = secret_key + secret_message
message_len = len(secret_message)

for i in range(message_len):
    message_char_val = ord(secret_message[i]) - ascii_offset
    key_char_val = ord(full_key[i]) - ascii_offset
    encrypted_char = chr(((message_char_val + key_char_val) % alphabet_len) + ascii_offset)
    encrypted_message += encrypted_char

print("Original Message: " + secret_message)
print("Secret Key: " + secret_key)
print("Encrypted Message: " + encrypted_message)
