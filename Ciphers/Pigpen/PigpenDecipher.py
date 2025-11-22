import argparse
from PIL import Image, ImageDraw
import numpy as np

parser = argparse.ArgumentParser(
    prog="PigpenDecipher",
    description="""Pigpen cipher decoder.
    Reads an image containing Pigpen symbols and converts them back to text.
    Supports multiple variants: standard, brierly1, brierly2, and templar."""
)

parser.add_argument('encrypted_image',
                    type=str,
                    help="Path to the encrypted image file")

parser.add_argument('-v', '--variant',
                    dest='variant',
                    type=str,
                    choices=['standard', 'brierly1', 'brierly2', 'templar'],
                    default='standard',
                    help="""Cipher variant to use:
                    standard - Traditional Pigpen arrangement (2 grids + 2 X shapes)
                    brierly1 - Thomas Brierly's grave first line (3 grids, no X shapes)
                    brierly2 - Thomas Brierly's grave second line (grid+X, then grid+X with dots)
                    templar - Knight's Templar (Maltese cross style)""")

args = parser.parse_args()

# Symbol dimensions (must match cipher script)
CELL_SIZE = 40
LINE_WIDTH = 3
DOT_RADIUS = 3

# Grid symbol types: which edges to draw (top, right, bottom, left)
GRID_SHAPES = {
    'grid_tl': (False, True, True, False),
    'grid_tc': (False, True, True, True),
    'grid_tr': (False, False, True, True),
    'grid_ml': (True, True, True, False),
    'grid_mc': (True, True, True, True),
    'grid_mr': (True, False, True, True),
    'grid_bl': (True, True, False, False),
    'grid_bc': (True, True, False, True),
    'grid_br': (True, False, False, True),
}

# Define letter mappings for each variant (same as cipher script)
VARIANTS = {
    'standard': {
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        'j': ('grid', 'grid_tl', 1), 'k': ('grid', 'grid_tc', 1), 'l': ('grid', 'grid_tr', 1),
        'm': ('grid', 'grid_ml', 1), 'n': ('grid', 'grid_mc', 1), 'o': ('grid', 'grid_mr', 1),
        'p': ('grid', 'grid_bl', 1), 'q': ('grid', 'grid_bc', 1), 'r': ('grid', 'grid_br', 1),
        's': ('x_wedge', 'top', 0), 'u': ('x_wedge', 'right', 0),
        'v': ('x_wedge', 'bottom', 0), 't': ('x_wedge', 'left', 0),
        'w': ('x_wedge', 'top', 1), 'y': ('x_wedge', 'right', 1),
        'z': ('x_wedge', 'bottom', 1), 'x': ('x_wedge', 'left', 1),
    },
    'brierly1': {
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        'j': ('grid', 'grid_tl', 1), 'k': ('grid', 'grid_tc', 1), 'l': ('grid', 'grid_tr', 1),
        'm': ('grid', 'grid_ml', 1), 'n': ('grid', 'grid_mc', 1), 'o': ('grid', 'grid_mr', 1),
        'p': ('grid', 'grid_bl', 1), 'q': ('grid', 'grid_bc', 1), 'r': ('grid', 'grid_br', 1),
        's': ('grid', 'grid_tl', 2), 't': ('grid', 'grid_tc', 2), 'u': ('grid', 'grid_tr', 2),
        'v': ('grid', 'grid_ml', 2), 'w': ('grid', 'grid_mc', 2), 'x': ('grid', 'grid_mr', 2),
        'y': ('grid', 'grid_bl', 2), 'z': ('grid', 'grid_bc', 2),
    },
    'brierly2': {
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        'j': ('x_wedge', 'top', 0), 'k': ('x_wedge', 'right', 0),
        'l': ('x_wedge', 'bottom', 0), 'm': ('x_wedge', 'left', 0),
        'n': ('grid', 'grid_tl', 1), 'o': ('grid', 'grid_tc', 1), 'p': ('grid', 'grid_tr', 1),
        'q': ('grid', 'grid_ml', 1), 'r': ('grid', 'grid_mc', 1), 's': ('grid', 'grid_mr', 1),
        't': ('grid', 'grid_bl', 1), 'u': ('grid', 'grid_bc', 1), 'v': ('grid', 'grid_br', 1),
        'w': ('x_wedge', 'top', 1), 'x': ('x_wedge', 'right', 1),
        'y': ('x_wedge', 'bottom', 1), 'z': ('x_wedge', 'left', 1),
    },
    'templar': {
        'a': ('x_wedge', 'top', 0), 'b': ('x_wedge', 'right', 0),
        'c': ('x_wedge', 'bottom', 0), 'd': ('x_wedge', 'left', 0),
        'f': ('plus_arm', 'right', 0), 'g': ('plus_arm', 'bottom', 0),
        'e': ('plus_arm', 'left', 0), 'h': ('plus_arm', 'top', 0),
        'i': ('plus_chevron', 'top', 0), 'j': ('plus_chevron', 'top', 0),
        'k': ('plus_chevron', 'right', 0), 'l': ('plus_chevron', 'bottom', 0),
        'm': ('plus_chevron', 'left', 0),
        'n': ('full_x', 'center', 0),
        'o': ('x_wedge', 'top', 1), 'p': ('x_wedge', 'right', 1),
        'q': ('x_wedge', 'bottom', 1), 'r': ('x_wedge', 'left', 1),
        's': ('plus_arm', 'top', 1), 't': ('plus_arm', 'right', 1),
        'u': ('plus_arm', 'bottom', 1), 'v': ('plus_arm', 'left', 1),
        'w': ('plus_chevron', 'bottom', 1), 'x': ('plus_chevron', 'top', 1),
        'y': ('plus_chevron', 'right', 1), 'z': ('plus_chevron', 'left', 1),
    },
}


def draw_grid_symbol(draw, x, y, shape_name, num_dots, size=CELL_SIZE):
    """Draw a grid-based Pigpen symbol."""
    edges = GRID_SHAPES[shape_name]
    top, right, bottom, left = edges

    margin = 8
    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    if top:
        draw.line([(x1, y1), (x2, y1)], fill='black', width=LINE_WIDTH)
    if right:
        draw.line([(x2, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
    if bottom:
        draw.line([(x1, y2), (x2, y2)], fill='black', width=LINE_WIDTH)
    if left:
        draw.line([(x1, y1), (x1, y2)], fill='black', width=LINE_WIDTH)

    cx, cy = x + size // 2, y + size // 2
    if num_dots == 1:
        draw.ellipse([(cx - DOT_RADIUS, cy - DOT_RADIUS),
                      (cx + DOT_RADIUS, cy + DOT_RADIUS)], fill='black')
    elif num_dots == 2:
        draw.ellipse([(cx - DOT_RADIUS - 5, cy - DOT_RADIUS),
                      (cx + DOT_RADIUS - 5, cy + DOT_RADIUS)], fill='black')
        draw.ellipse([(cx - DOT_RADIUS + 5, cy - DOT_RADIUS),
                      (cx + DOT_RADIUS + 5, cy + DOT_RADIUS)], fill='black')


def draw_x_wedge(draw, x, y, direction, num_dots, size=CELL_SIZE):
    """Draw an X-based wedge shape."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    if direction == 'bottom':
        draw.line([(cx, y1), (x1, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy + 3
    elif direction == 'left':
        draw.line([(x2, cy), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x2, cy), (x1, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx - 3, cy
    elif direction == 'top':
        draw.line([(cx, y2), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y2), (x2, y1)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy - 3
    elif direction == 'right':
        draw.line([(x1, cy), (x2, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, cy), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx + 3, cy

    if num_dots >= 1:
        draw.ellipse([(dot_cx - DOT_RADIUS, dot_cy - DOT_RADIUS),
                      (dot_cx + DOT_RADIUS, dot_cy + DOT_RADIUS)], fill='black')


def draw_plus_arm(draw, x, y, direction, num_dots, size=CELL_SIZE):
    """Draw a full triangle pointing in a direction (for Templar HFGE, STUV)."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    # Draw full triangle (like x_wedge but with base closed)
    if direction == 'bottom':
        # Triangle pointing up: apex at top, base at bottom
        draw.line([(cx, y1), (x1, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, y2), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy + 3
    elif direction == 'left':
        # Triangle pointing right: apex at right, base at left
        draw.line([(x2, cy), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x2, cy), (x1, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, y1), (x1, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx - 3, cy
    elif direction == 'top':
        # Triangle pointing down: apex at bottom, base at top
        draw.line([(cx, y2), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y2), (x2, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, y1), (x2, y1)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy - 3
    elif direction == 'right':
        # Triangle pointing left: apex at left, base at right
        draw.line([(x1, cy), (x2, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, cy), (x2, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(x2, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx + 3, cy

    if num_dots >= 1:
        draw.ellipse([(dot_cx - DOT_RADIUS, dot_cy - DOT_RADIUS),
                      (dot_cx + DOT_RADIUS, dot_cy + DOT_RADIUS)], fill='black')


def draw_plus_chevron(draw, x, y, direction, num_dots, size=CELL_SIZE):
    """Draw a kite shape (top-heavy diamond) for Templar I/J-M, W-Z."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    # Kite shape: shorter distance to top point, longer to bottom point
    # The "top" of the kite (shorter side) faces the direction
    short_dist = 6   # distance from center to the short tip
    long_dist = 14   # distance from center to the long tip
    width_dist = 10  # distance from center to side points

    if direction == 'top':
        # Kite pointing up: short tip at top, long tip at bottom
        points = [
            (cx, cy - short_dist),      # top (short)
            (cx + width_dist, cy),      # right
            (cx, cy + long_dist),       # bottom (long)
            (cx - width_dist, cy),      # left
        ]
        dot_cx, dot_cy = cx, cy + 6
    elif direction == 'right':
        # Kite pointing right: short tip at right, long tip at left
        points = [
            (cx + short_dist, cy),      # right (short)
            (cx, cy + width_dist),      # bottom
            (cx - long_dist, cy),       # left (long)
            (cx, cy - width_dist),      # top
        ]
        dot_cx, dot_cy = cx - 6, cy
    elif direction == 'bottom':
        # Kite pointing down: short tip at bottom, long tip at top
        points = [
            (cx, cy + short_dist),      # bottom (short)
            (cx - width_dist, cy),      # left
            (cx, cy - long_dist),       # top (long)
            (cx + width_dist, cy),      # right
        ]
        dot_cx, dot_cy = cx, cy - 6
    elif direction == 'left':
        # Kite pointing left: short tip at left, long tip at right
        points = [
            (cx - short_dist, cy),      # left (short)
            (cx, cy - width_dist),      # top
            (cx + long_dist, cy),       # right (long)
            (cx, cy + width_dist),      # bottom
        ]
        dot_cx, dot_cy = cx + 6, cy

    draw.polygon(points, outline='black', width=LINE_WIDTH)

    if num_dots >= 1:
        draw.ellipse([(dot_cx - DOT_RADIUS, dot_cy - DOT_RADIUS),
                      (dot_cx + DOT_RADIUS, dot_cy + DOT_RADIUS)], fill='black')


def draw_full_x(draw, x, y, direction, num_dots, size=CELL_SIZE):
    """Draw a complete X shape."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    draw.line([(x1, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
    draw.line([(x1, y2), (x2, y1)], fill='black', width=LINE_WIDTH)

    if num_dots >= 1:
        draw.ellipse([(cx - DOT_RADIUS, cy - DOT_RADIUS),
                      (cx + DOT_RADIUS, cy + DOT_RADIUS)], fill='black')


def generate_reference_symbol(letter, variant):
    """Generate a reference symbol image for a given letter."""
    mapping = VARIANTS[variant]
    if letter not in mapping:
        return None

    symbol_type, direction, num_dots = mapping[letter]

    img = Image.new('RGB', (CELL_SIZE, CELL_SIZE), 'white')
    draw = ImageDraw.Draw(img)

    if symbol_type == 'grid':
        draw_grid_symbol(draw, 0, 0, direction, num_dots)
    elif symbol_type == 'x_wedge':
        draw_x_wedge(draw, 0, 0, direction, num_dots)
    elif symbol_type == 'plus_arm':
        draw_plus_arm(draw, 0, 0, direction, num_dots)
    elif symbol_type == 'plus_chevron':
        draw_plus_chevron(draw, 0, 0, direction, num_dots)
    elif symbol_type == 'full_x':
        draw_full_x(draw, 0, 0, direction, num_dots)

    return img


def get_content_bbox(img, threshold=240):
    """Get the bounding box of the actual content in an image."""
    gray = img.convert('L')
    pixels = np.array(gray)

    content_mask = pixels < threshold

    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)

    if not np.any(rows) or not np.any(cols):
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
    left, top, right, bottom = get_content_bbox(img)

    content = img.crop((left, top, right, bottom))
    content_width = right - left
    content_height = bottom - top

    centered = Image.new('RGB', (target_width, target_height), 'white')

    paste_x = (target_width - content_width) // 2
    paste_y = (target_height - content_height) // 2

    centered.paste(content, (paste_x, paste_y))

    return centered


def detect_character_boundaries(img, min_gap=5, threshold=240):
    """Detect character boundaries by scanning for vertical gaps."""
    gray = img.convert('L')
    pixels = np.array(gray)

    col_has_content = np.any(pixels < threshold, axis=0)

    # First pass: detect raw boundaries
    raw_boundaries = []
    in_character = False
    char_start = 0

    for col_idx, has_content in enumerate(col_has_content):
        if has_content and not in_character:
            char_start = col_idx
            in_character = True
        elif not has_content and in_character:
            if col_idx - char_start >= 3:
                raw_boundaries.append((char_start, col_idx))
            in_character = False

    if in_character and img.width - char_start >= 3:
        raw_boundaries.append((char_start, img.width))

    # Second pass: merge nearby boundaries (to handle dots as part of symbols)
    # Merge if gap between boundaries is less than min_merge_gap
    min_merge_gap = 10  # pixels
    if not raw_boundaries:
        return []

    merged_boundaries = [raw_boundaries[0]]
    for left, right in raw_boundaries[1:]:
        prev_left, prev_right = merged_boundaries[-1]
        gap = left - prev_right

        if gap < min_merge_gap:
            # Merge with previous boundary
            merged_boundaries[-1] = (prev_left, right)
        else:
            merged_boundaries.append((left, right))

    return merged_boundaries


def compare_images(img1, img2):
    """Compare two images and return a similarity score (lower is better)."""
    canvas_width = max(img1.width, img2.width)
    canvas_height = max(img1.height, img2.height)

    centered1 = center_image_content(img1, canvas_width, canvas_height)
    centered2 = center_image_content(img2, canvas_width, canvas_height)

    pixels1 = list(centered1.convert('RGB').getdata())
    pixels2 = list(centered2.convert('RGB').getdata())

    total_error = 0
    for p1, p2 in zip(pixels1, pixels2):
        for c1, c2 in zip(p1, p2):
            total_error += (c1 - c2) ** 2

    mse = total_error / (len(pixels1) * 3)
    return mse


# Load the encrypted image
try:
    encrypted_img = Image.open(args.encrypted_image)
except FileNotFoundError:
    print(f"Error: Could not find encrypted image at {args.encrypted_image}")
    exit(1)

variant = args.variant

# Get all unique letters for this variant (excluding duplicates like i/j in templar)
letters = list(VARIANTS[variant].keys())
# Remove 'j' from templar since it's the same as 'i'
if variant == 'templar':
    letters = [l for l in letters if l != 'j']

# Generate reference symbols
print(f"Generating reference symbols for variant: {variant}")
reference_symbols = {}
for letter in letters:
    symbol = generate_reference_symbol(letter, variant)
    if symbol:
        reference_symbols[letter] = symbol

# Detect character boundaries
print("Detecting character boundaries...")
char_boundaries = detect_character_boundaries(encrypted_img)

if len(char_boundaries) == 0:
    print("Error: No characters detected in the encrypted image.")
    exit(1)

print(f"Detected {len(char_boundaries)} character(s)")

# Decode each symbol
enc_height = encrypted_img.size[1]
decrypted_message = ""

for idx, (left, right) in enumerate(char_boundaries):
    current_symbol = encrypted_img.crop((left, 0, right, enc_height))

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
print(f"Variant: {variant}")
print(f"Encrypted image: {args.encrypted_image}")
print(f"Number of symbols detected: {len(char_boundaries)}")
print(f"Decrypted message: {decrypted_message}")
