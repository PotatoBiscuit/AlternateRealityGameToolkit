import argparse

parser = argparse.ArgumentParser(
    prog="CaesarDecipher",
    description="Decipher script for the Caesar Cipher. Shifts each letter back by the specified number of positions"
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")
parser.add_argument('-s', '--shift',
                    dest="shift",
                    required=True,
                    type=int,
                    help="Number of positions the letters were shifted")

args = parser.parse_args()

encrypted_message = args.encrypted_message
decrypted_message = ""
shift = args.shift % 26

for char in encrypted_message:
    if char.isalpha():
        ascii_offset = 97 if char.islower() else 65
        x = ord(char) - ascii_offset
        decrypted_message += chr(((x - shift) % 26) + ascii_offset)
    else:
        decrypted_message += char

print("Shift=" + str(shift))
print()
print("Encrypted message: " + encrypted_message)
print("Decrypted message: " + decrypted_message)
