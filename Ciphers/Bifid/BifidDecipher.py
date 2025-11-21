import argparse
import csv

parser = argparse.ArgumentParser(
    prog="BifidDecipher",
    description="""Decipher script for the Bifid cipher. Reverses the fractionation process by converting
    ciphertext to coordinates, splitting them into rows and columns, then pairing them to recover
    the original plaintext. Requires the same Polybius square used for encryption."""
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")

parser.add_argument('-s', '--square',
                    type=str,
                    required=True,
                    help="Path to a CSV file containing the 5x5 Polybius square used for encryption")

args = parser.parse_args()

encrypted_message = args.encrypted_message.replace(" ", "").lower().replace("j", "i")

# Load the 5x5 Polybius square from CSV
alphabet = "abcdefghiklmnopqrstuvwxyz"  # 25 letters, no j

square = ""
with open(args.square, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        for cell in row:
            square += cell.lower().replace("j", "i")

if len(square) != 25 or set(square) != set(alphabet):
    print("Error: CSV must contain exactly 25 unique letters (no J)")
    exit(1)

# Create lookup dictionaries
char_to_coords = {}
coords_to_char = {}
for idx, char in enumerate(square):
    row = idx // 5
    col = idx % 5
    char_to_coords[char] = (row, col)
    coords_to_char[(row, col)] = char

# Convert ciphertext to coordinates
combined = []
for char in encrypted_message:
    if char in char_to_coords:
        row, col = char_to_coords[char]
        combined.append(row)
        combined.append(col)

# Split combined coordinates: first half are rows, second half are cols
mid = len(combined) // 2
rows = combined[:mid]
cols = combined[mid:]

# Pair up rows and cols to get original coordinates
decrypted_message = ""
for i in range(len(rows)):
    row = rows[i]
    col = cols[i]
    decrypted_message += coords_to_char[(row, col)]

print("Encrypted Message: " + encrypted_message)
print("Polybius Square:")
for i in range(5):
    print("  " + " ".join(square[i*5:(i+1)*5]))
print("Decrypted Message: " + decrypted_message)
