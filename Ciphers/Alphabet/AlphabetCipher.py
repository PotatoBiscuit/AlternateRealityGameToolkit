import argparse

alphabet_len = 26

parser = argparse.ArgumentParser(
    prog="AlphabetCipher",
    description="""Made by Lewis Carroll in 1868, it encodes messages by taking a repeated secret key as
    well as the original message to find the correct encrypted letter in a tabula recta, which in this case
    is just the alphabet but shifted to the left once for each row"""
)

parser.add_argument('secret_message',
                        type=str,
                        help="Message to encipher")

parser.add_argument('secret_key',
                        type=str,
                        help="Key used to encrypt the message")

args = parser.parse_args()

secret_message = args.secret_message.replace(" ","").lower()
secret_key = args.secret_key.replace(" ","").lower()

secret_key_len = len( secret_key )

ascii_offset = 97
encrypted_message = ""

key_ind = 0
for character in secret_message:
    encrypted_message += chr((( ( ord(character) - ascii_offset ) + ( ord(secret_key[key_ind]) - ascii_offset ) ) % alphabet_len) + ascii_offset)
    key_ind = ( key_ind + 1 ) % secret_key_len

print( "Original Message: " + secret_message )
print( "Secret Key: " + secret_key )
print( "Encrypted Message: " + encrypted_message )
