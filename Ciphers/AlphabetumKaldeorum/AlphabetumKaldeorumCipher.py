import argparse
from PIL import Image
import os

parser = argparse.ArgumentParser(
    prog="AlphabetumKaldeoruмCipher",
    description="""Medieval substitution cipher from 1428, also known as the Alphabet of the Chaldeans.
    Converts text to symbolic characters and outputs as an image since the symbols don't exist in Unicode.
    Note: j is treated as i, and u/v are equivalent in the original cipher."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('-o', '--output',
                    dest='output_file',
                    type=str,
                    default='kaldeorum_encrypted.png',
                    help="Output image file (default: kaldeorum_encrypted.png)")

args = parser.parse_args()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
reference_image_path = os.path.join(script_dir, '..', 'Alphabetum_Kaldeorum.jpg')

# Load the reference image containing all symbols
try:
    reference_img = Image.open(reference_image_path)
except FileNotFoundError:
    print(f"Error: Could not find reference image at {reference_image_path}")
    print("Please ensure Alphabetum_Kaldeorum.jpg is in the repository root.")
    exit(1)

# Define the grid positions for each symbol in the reference image
# The image has symbols arranged in a grid with 8 columns
# Row 1: a, b, c, d, e, f, g, h
# Row 2: i, k, l, m, n, o, p, q
# Row 3: r, s, t, u/v, x, y, z

# Calculate cell dimensions based on the image
img_width, img_height = reference_img.size

# The grid starts after the title (approximately 140 pixels from top)
# and has 3 rows of symbols
grid_top = 175
grid_left = 40
cell_width = 111
column_gap = 9
label_height = 50
cell_height = 50
row_gap = 36
third_row_offset = 58

left_margin = 2

# Coordinates for each letter (column, row)
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

def extract_symbol(letter):
    """Extract the symbol for a given letter from the reference image."""
    letter = letter.lower()
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

# Process the message
secret_message = args.secret_message.lower()
# Handle 'w' as double 'v' per medieval convention
secret_message = secret_message.replace('w', 'vv')
secret_message = ''.join(c for c in secret_message if c.isalpha())  # Keep only letters

if not secret_message:
    print("Error: Message contains no valid letters to encode.")
    exit(1)

# Extract symbols for each letter
symbols = []
for char in secret_message:
    symbol = extract_symbol(char)
    if symbol:
        symbols.append(symbol)

if not symbols:
    print("Error: Could not extract any symbols.")
    exit(1)

# Create output image by arranging symbols horizontally
symbol_width = cell_width
symbol_height = cell_height
output_width = symbol_width * len(symbols)
output_height = symbol_height

output_img = Image.new('RGB', (output_width, output_height), 'white')

# Paste each symbol into the output image
for i, symbol in enumerate(symbols):
    x = i * symbol_width
    output_img.paste(symbol, (x, 0))

# Save the output image
output_img.save(args.output_file)

print(f"Original Message: {secret_message}")
print(f"Encrypted message saved to: {args.output_file}")
print(f"Number of symbols: {len(symbols)}")
