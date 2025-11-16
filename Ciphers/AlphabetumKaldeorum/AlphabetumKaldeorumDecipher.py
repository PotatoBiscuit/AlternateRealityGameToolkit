import argparse
from PIL import Image, ImageChops
import os
import numpy as np

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

def get_content_bbox(img, threshold=240):
    """Get the bounding box of the actual content (non-background) in an image."""
    # Convert to grayscale and numpy array
    gray = img.convert('L')
    pixels = np.array(gray)

    # Find all pixels darker than threshold (assuming white/light background)
    content_mask = pixels < threshold

    # Find rows and columns that contain content
    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)

    # Find the bounding box
    if not np.any(rows) or not np.any(cols):
        # No content found, return full image bounds
        return (0, 0, img.width, img.height)

    row_indices = np.where(rows)[0]
    col_indices = np.where(cols)[0]

    top = row_indices[0]
    bottom = row_indices[-1] + 1
    left = col_indices[0]
    right = col_indices[-1] + 1

    return (left, top, right, bottom)

def center_image_content(img, target_width, target_height):
    """Center the actual content of an image within a canvas of target size."""
    # Get the bounding box of the content
    left, top, right, bottom = get_content_bbox(img)

    # Crop to content
    content = img.crop((left, top, right, bottom))
    content_width = right - left
    content_height = bottom - top

    # Create a white canvas of target size
    centered = Image.new('RGB', (target_width, target_height), 'white')

    # Calculate position to paste content in the center
    paste_x = (target_width - content_width) // 2
    paste_y = (target_height - content_height) // 2

    # Paste the content
    centered.paste(content, (paste_x, paste_y))

    return centered

def detect_character_boundaries(img, min_gap=5, threshold=240):
    """
    Detect character boundaries by scanning for vertical gaps.
    Returns a list of (left, right) tuples for each detected character.
    """
    # Convert to grayscale
    gray = img.convert('L')
    pixels = np.array(gray)

    # Find columns that contain any non-background pixels
    col_has_content = np.any(pixels < threshold, axis=0)

    # Find transitions from background to content and vice versa
    boundaries = []
    in_character = False
    char_start = 0

    for col_idx, has_content in enumerate(col_has_content):
        if has_content and not in_character:
            # Start of a new character
            char_start = col_idx
            in_character = True
        elif not has_content and in_character:
            # End of current character
            # Only record if we have some minimum width
            if col_idx - char_start >= 3:
                boundaries.append((char_start, col_idx))
            in_character = False

    # Handle case where image ends while still in a character
    if in_character and img.width - char_start >= 3:
        boundaries.append((char_start, img.width))

    return boundaries

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
    """
    Compare two images and return a similarity score (lower is better).
    Centers both images on a common canvas size before comparison.
    """
    # Determine a common canvas size (use the larger dimensions)
    canvas_width = max(img1.width, img2.width)
    canvas_height = max(img1.height, img2.height)

    # Center both images on canvases of the same size
    centered1 = center_image_content(img1, canvas_width, canvas_height)
    centered2 = center_image_content(img2, canvas_width, canvas_height)

    # Convert to RGB and get pixel data
    pixels1 = list(centered1.convert('RGB').getdata())
    pixels2 = list(centered2.convert('RGB').getdata())

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

# Auto-detect character boundaries
print("Auto-detecting character boundaries...")
char_boundaries = detect_character_boundaries(encrypted_img)

if len(char_boundaries) == 0:
    print("Error: No characters detected in the encrypted image.")
    print("The image may be too light, too small, or have no content.")
    exit(1)

print(f"Detected {len(char_boundaries)} character(s)")

# Decode each symbol
decrypted_message = ""

for idx, (left, right) in enumerate(char_boundaries):
    # Extract the current symbol from encrypted image
    # Use full height or a reasonable max
    top = 0
    bottom = enc_height

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
        print(f"Character {idx + 1}: '{best_match}' (score: {best_score:.1f})")

print()
print(f"Encrypted image: {args.encrypted_image}")
print(f"Number of symbols detected: {len(char_boundaries)}")
print(f"Decrypted message: {decrypted_message}")
print()
print("Note: In medieval Latin, 'u' and 'v' were equivalent, 'j' was written as 'i',")
print("and 'w' was written as 'vv'. You may need to interpret the output accordingly.")
