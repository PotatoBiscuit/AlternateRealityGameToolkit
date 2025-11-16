import argparse

from math import gcd as bltin_gcd

def coprime(a, b):
    return bltin_gcd(a, b) == 1

def mod_inverse(a, m):
    """Find the modular multiplicative inverse of a mod m using Extended Euclidean Algorithm"""
    if not coprime(a, m):
        raise ValueError("a and m must be coprime")

    # Extended Euclidean Algorithm
    r, x0, x1 = m, 1, 0
    while a > 1:
        q = a // r
        r, a = a % r, r
        x0, x1 = x1, x0 - q * x1

    return x0 + m if x0 < 0 else x0

parser = argparse.ArgumentParser(
    prog="AffineDecipher",
    description="Decipher script for the Affine Cipher. Uses the inverse formula: x = a^(-1) * (y - b) mod 26"
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")
parser.add_argument('-a',
                    dest="a",
                    required=True,
                    type=int,
                    help="a value used in the affine function (must be coprime to 26)")
parser.add_argument('-b',
                    dest="b",
                    required=True,
                    type=int,
                    help="b value used in the affine function")

args = parser.parse_args()

encrypted_message = args.encrypted_message
decrypted_message = ""

m = 26
ascii_offset = 97
a = args.a
b = args.b

# Verify that a is coprime to m
if not coprime(a, m):
    print(f"Error: a={a} is not coprime to m={m}. Decryption is not possible.")
    exit(1)

# Find the modular multiplicative inverse of a
a_inv = mod_inverse(a, m)

for char in encrypted_message:
    y = ord(char) - ascii_offset
    x = (a_inv * (y - b)) % m
    decrypted_message += chr(x + ascii_offset)

print("a=" + str(a))
print("b=" + str(b))
print("a^(-1)=" + str(a_inv))
print()
print("Encrypted message: " + encrypted_message)
print("Decrypted message: " + decrypted_message)
