import argparse
from PIL import Image
import os

parser = argparse.ArgumentParser(
    prog="AlphabetumKaldeoruмDecipher",
    description="""Decipher script for the Alphabetum Kaldeorum medieval cipher.
    Reads an image containing Kaldeorum symbols and converts them back to text.
    Note: 'vv' will be displayed as is (historically represents 'w')."""
)

parser.add_argument('encrypted_image',
                    type=str,
                    help="Path to the encrypted image file")

args = parser.parse_args()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
reference_image_path = os.path.join(script_dir, 'Alphabetum_Kaldeorum.jpg')

# Load the reference image containing all symbols
try:
    reference_img = Image.open(reference_image_path)
except FileNotFoundError:
    print(f"Error: Could not find reference image at {reference_image_path}")
    print("Please ensure Alphabetum_Kaldeorum.jpg is in the repository root.")
    exit(1)

# Load the encrypted image
try:
    encrypted_img = Image.open(args.encrypted_image)
except FileNotFoundError:
    print(f"Error: Could not find encrypted image at {args.encrypted_image}")
    exit(1)

# Define grid parameters (same as cipher script)
grid_top = 175
grid_left = 40
cell_width = 111
column_gap = 9
label_height = 50
cell_height = 50
row_gap = 36
third_row_offset = 58

left_margin = 2

# All letters in the alphabet (in order they appear in the reference)
letters = [
    'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
    'i', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
    'r', 's', 't', 'v', 'x', 'y', 'z'  # using 'v' for u/v
]

# Coordinates for each letter (column, row, num_chars)
symbol_positions = {
    'a': (0, 0, 1), 'b': (1, 0, 1), 'c': (2, 0, 1), 'd': (3, 0, 1),
    'e': (4, 0, 1), 'f': (5, 0, 1), 'g': (6, 0, 2), 'h': (7, 0, 2.5),
    'i': (0, 1, 1), 'j': (0, 1, 1),  # j maps to i
    'k': (1, 1, 1), 'l': (2, 1, 2), 'm': (3, 1, 1), 'n': (4, 1, 1),
    'o': (5, 1, 2), 'p': (6, 1, 2), 'q': (7, 1, 2),
    'r': (0, 2, 1), 's': (1, 2, 1), 't': (2, 2, 1),
    'u': (3, 2, 1), 'v': (3, 2, 1),  # u and v share same symbol
    'x': (4, 2, 1), 'y': (5, 2, 1), 'z': (6, 2, 1)
}

def extract_reference_symbol(letter):
    """Extract the symbol for a given letter from the reference image."""
    if letter not in symbol_positions:
        return None

    col, row, num_chars = symbol_positions[letter]
    left = grid_left + col * (cell_width + column_gap)
    if row == 2:
        left += third_row_offset
    top = grid_top + row * (cell_height + row_gap) + (row + 1) * label_height
    right = left + round(cell_width / num_chars)
    bottom = top + cell_height

    symbol = reference_img.crop((left + left_margin, top, right, bottom))
    return symbol

def compare_images(img1, img2):
    """Compare two images and return a similarity score (lower is better)."""
    # Ensure images are the same size
    if img1.size != img2.size:
        img2 = img2.resize(img1.size)

    # Convert to RGB and get pixel data
    pixels1 = list(img1.convert('RGB').getdata())
    pixels2 = list(img2.convert('RGB').getdata())

    # Calculate mean squared error
    total_error = 0
    for p1, p2 in zip(pixels1, pixels2):
        # Each pixel is (R, G, B)
        for c1, c2 in zip(p1, p2):
            total_error += (c1 - c2) ** 2

    mse = total_error / (len(pixels1) * 3)
    return mse

# Extract all reference symbols
reference_symbols = {}
for letter in letters:
    symbol = extract_reference_symbol(letter)
    if symbol:
        reference_symbols[letter] = symbol

# Get dimensions of encrypted image
enc_width, enc_height = encrypted_img.size

# Calculate number of symbols in the encrypted image
# Assuming symbols are arranged horizontally with same width
num_symbols = enc_width // cell_width

if num_symbols == 0:
    print("Error: Encrypted image is too small to contain any symbols.")
    exit(1)

# Decode each symbol
decrypted_message = ""

for i in range(num_symbols):
    # Extract the current symbol from encrypted image
    left = i * cell_width
    top = 0
    right = left + cell_width
    bottom = min(cell_height, enc_height)

    current_symbol = encrypted_img.crop((left, top, right, bottom))

    # Find the best match among reference symbols
    best_match = None
    best_score = float('inf')

    for letter, ref_symbol in reference_symbols.items():
        score = compare_images(current_symbol, ref_symbol)
        if score < best_score:
            best_score = score
            best_match = letter

    if best_match:
        decrypted_message += best_match

print(f"Encrypted image: {args.encrypted_image}")
print(f"Number of symbols detected: {num_symbols}")
print(f"Decrypted message: {decrypted_message}")
print()
print("Note: In medieval Latin, 'u' and 'v' were equivalent, 'j' was written as 'i',")
print("and 'w' was written as 'vv'. You may need to interpret the output accordingly.")
