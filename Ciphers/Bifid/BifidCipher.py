import argparse
import random
import csv

parser = argparse.ArgumentParser(
    prog="BifidCipher",
    description="""The Bifid cipher is a digraphic substitution cipher invented by Felix Delastelle in 1901.
    It combines the Polybius square with transposition and fractionation. Each letter is converted to
    row/column coordinates, then the coordinates are rearranged and converted back to letters. This uses
    a 5x5 grid where I and J share a position."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('-s', '--square',
                    type=str,
                    default=None,
                    help="Path to a CSV file containing a 5x5 Polybius square. If not provided, a random one is generated.")

args = parser.parse_args()

secret_message = args.secret_message.replace(" ", "").lower().replace("j", "i")

# Build or load the 5x5 Polybius square
alphabet = "abcdefghiklmnopqrstuvwxyz"  # 25 letters, no j

if args.square:
    # Load square from CSV file
    square = ""
    with open(args.square, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            for cell in row:
                square += cell.lower().replace("j", "i")

    if len(square) != 25 or set(square) != set(alphabet):
        print("Error: CSV must contain exactly 25 unique letters (no J)")
        exit(1)
else:
    # Generate a random Polybius square
    letters = list(alphabet)
    random.shuffle(letters)
    square = "".join(letters)

# Create lookup dictionaries
char_to_coords = {}
coords_to_char = {}
for idx, char in enumerate(square):
    row = idx // 5
    col = idx % 5
    char_to_coords[char] = (row, col)
    coords_to_char[(row, col)] = char

# Convert message to coordinates
rows = []
cols = []
for char in secret_message:
    if char in char_to_coords:
        row, col = char_to_coords[char]
        rows.append(row)
        cols.append(col)

# Combine: all rows followed by all cols
combined = rows + cols

# Take pairs and convert back to letters
encrypted_message = ""
for i in range(0, len(combined), 2):
    row = combined[i]
    col = combined[i + 1]
    encrypted_message += coords_to_char[(row, col)]

print("Original Message: " + secret_message)
print("Polybius Square:")
for i in range(5):
    print("  " + " ".join(square[i*5:(i+1)*5]))
print("Encrypted Message: " + encrypted_message)
