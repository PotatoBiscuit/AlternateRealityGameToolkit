import argparse, random

from math import gcd as bltin_gcd

def coprime(a, b):
    return bltin_gcd(a, b) == 1

parser = argparse.ArgumentParser(
    prog="AffineCipher",
    description="Cipher that converts each character to an associated int, and puts it through the '(ax+b) mod 26' formula"
)

parser.add_argument('secret_message',
                        type=str,
                        help="Message to encipher")
parser.add_argument('-a',
                        dest="a",
                        type=int,
                        help="a value in affine function, MUST be coprime to m (26)")
parser.add_argument('-b',
                        dest="b",
                        type=int,
                        help="b value in affine function")

args = parser.parse_args()

secret_message = args.secret_message
encrypted_message = ""

m = 26
ascii_offset = 97
a = 0
b = 0

if args.a is not None:
    a = args.a
else:
    a = random.randrange( 10000,1000000 )
    while not coprime( a, m ):
        a = random.randrange( 10000,1000000 )

if args.b is not None:
    b = args.b
else:
    b = random.randrange( 10000,1000000 )

for char in secret_message:
    x = ord( char ) - ascii_offset
    encrypted_message += chr(((a * x + b) % m) + ascii_offset)

print("a=" + str(a))
print("b=" + str(b))
print()
print("Original message: " + secret_message )
print("Encrypted message: " + encrypted_message )