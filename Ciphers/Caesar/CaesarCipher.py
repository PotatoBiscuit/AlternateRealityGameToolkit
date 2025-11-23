import argparse

parser = argparse.ArgumentParser(
    prog="CaesarCipher",
    description="Cipher that shifts each letter by a fixed number of positions in the alphabet. Originally used by Julius Caesar,
    who typically used it with a shift of three to protect military secrets."
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")
parser.add_argument('-s', '--shift',
                    dest="shift",
                    required=True,
                    type=int,
                    help="Number of positions to shift each letter")

args = parser.parse_args()

secret_message = args.secret_message
encrypted_message = ""
shift = args.shift % 26

for char in secret_message:
    if char.isalpha():
        ascii_offset = 97 if char.islower() else 65
        x = ord(char) - ascii_offset
        encrypted_message += chr(((x + shift) % 26) + ascii_offset)
    else:
        encrypted_message += char

print("Shift=" + str(shift))
print()
print("Original message: " + secret_message)
print("Encrypted message: " + encrypted_message)
