import argparse
from PIL import Image, ImageDraw

parser = argparse.ArgumentParser(
    prog="PigpenCipher",
    description="""Pigpen cipher (also known as Freemason's cipher) encoder.
    Converts text to Pigpen symbols and outputs as an image.
    Supports multiple variants: standard, brierly1, brierly2, and templar."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('-o', '--output',
                    dest='output_file',
                    type=str,
                    default='pigpen_encrypted.png',
                    help="Output image file (default: pigpen_encrypted.png)")

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

# Symbol dimensions
CELL_SIZE = 40
LINE_WIDTH = 3
DOT_RADIUS = 3
SPACE_WIDTH = 20

# Grid symbol types: which edges to draw (top, right, bottom, left)
GRID_SHAPES = {
    'grid_tl': (False, True, True, False),    # top-left: right, bottom
    'grid_tc': (False, True, True, True),     # top-center: left, right, bottom
    'grid_tr': (False, False, True, True),    # top-right: left, bottom
    'grid_ml': (True, True, True, False),     # middle-left: top, right, bottom
    'grid_mc': (True, True, True, True),      # middle-center: all sides (box)
    'grid_mr': (True, False, True, True),     # middle-right: top, left, bottom
    'grid_bl': (True, True, False, False),    # bottom-left: top, right
    'grid_bc': (True, True, False, True),     # bottom-center: top, left, right
    'grid_br': (True, False, False, True),    # bottom-right: top, left
}

# X symbol directions
X_DIRECTIONS = ['top', 'right', 'bottom', 'left']

# Templar symbol types
TEMPLAR_TYPES = {
    'x_wedge': 'x_wedge',           # V-shaped wedge from X
    'plus_arm': 'plus_arm',         # Single arm of + cross
    'plus_chevron': 'plus_chevron', # Arm with arrowhead
    'full_x': 'full_x',             # Complete X shape
}

# Define letter mappings for each variant
VARIANTS = {
    # Standard Pigpen: 2 grids (A-I, J-R with dots) + 2 X shapes (S-V, W-Z with dots)
    'standard': {
        # First grid (no dot): A-I
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        # Second grid (1 dot): J-R
        'j': ('grid', 'grid_tl', 1), 'k': ('grid', 'grid_tc', 1), 'l': ('grid', 'grid_tr', 1),
        'm': ('grid', 'grid_ml', 1), 'n': ('grid', 'grid_mc', 1), 'o': ('grid', 'grid_mr', 1),
        'p': ('grid', 'grid_bl', 1), 'q': ('grid', 'grid_bc', 1), 'r': ('grid', 'grid_br', 1),
        # First X (no dot): S-V
        's': ('x_wedge', 'top', 0), 'u': ('x_wedge', 'right', 0),
        'v': ('x_wedge', 'bottom', 0), 't': ('x_wedge', 'left', 0),
        # Second X (1 dot): W-Z
        'w': ('x_wedge', 'top', 1), 'y': ('x_wedge', 'right', 1),
        'z': ('x_wedge', 'bottom', 1), 'x': ('x_wedge', 'left', 1),
    },

    # Brierly1: 3 grids only (no X shapes), last position of 3rd grid unused
    # Grid 1 (no dot): A-I, Grid 2 (1 dot): J-R, Grid 3 (2 dots): S-Z
    'brierly1': {
        # First grid (no dot): A-I
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        # Second grid (1 dot): J-R
        'j': ('grid', 'grid_tl', 1), 'k': ('grid', 'grid_tc', 1), 'l': ('grid', 'grid_tr', 1),
        'm': ('grid', 'grid_ml', 1), 'n': ('grid', 'grid_mc', 1), 'o': ('grid', 'grid_mr', 1),
        'p': ('grid', 'grid_bl', 1), 'q': ('grid', 'grid_bc', 1), 'r': ('grid', 'grid_br', 1),
        # Third grid (2 dots): S-Z (only 8 letters, grid_br unused)
        's': ('grid', 'grid_tl', 2), 't': ('grid', 'grid_tc', 2), 'u': ('grid', 'grid_tr', 2),
        'v': ('grid', 'grid_ml', 2), 'w': ('grid', 'grid_mc', 2), 'x': ('grid', 'grid_mr', 2),
        'y': ('grid', 'grid_bl', 2), 'z': ('grid', 'grid_bc', 2),
    },

    # Brierly2: Grid+X for A-M (no dots), then Grid+X for N-Z (with dots)
    'brierly2': {
        # First grid (no dot): A-I
        'a': ('grid', 'grid_tl', 0), 'b': ('grid', 'grid_tc', 0), 'c': ('grid', 'grid_tr', 0),
        'd': ('grid', 'grid_ml', 0), 'e': ('grid', 'grid_mc', 0), 'f': ('grid', 'grid_mr', 0),
        'g': ('grid', 'grid_bl', 0), 'h': ('grid', 'grid_bc', 0), 'i': ('grid', 'grid_br', 0),
        # First X (no dot): J-M
        'j': ('x_wedge', 'top', 0), 'k': ('x_wedge', 'right', 0),
        'l': ('x_wedge', 'bottom', 0), 'm': ('x_wedge', 'left', 0),
        # Second grid (1 dot): N-V
        'n': ('grid', 'grid_tl', 1), 'o': ('grid', 'grid_tc', 1), 'p': ('grid', 'grid_tr', 1),
        'q': ('grid', 'grid_ml', 1), 'r': ('grid', 'grid_mc', 1), 's': ('grid', 'grid_mr', 1),
        't': ('grid', 'grid_bl', 1), 'u': ('grid', 'grid_bc', 1), 'v': ('grid', 'grid_br', 1),
        # Second X (1 dot): W-Z
        'w': ('x_wedge', 'top', 1), 'x': ('x_wedge', 'right', 1),
        'y': ('x_wedge', 'bottom', 1), 'z': ('x_wedge', 'left', 1),
    },

    # Knight's Templar: Based on Maltese cross components
    # X wedges (A-D), + arms (E-H), + chevrons (I/J-M), full X (N),
    # X wedges+dot (O-R), + arms+dot (S-V), + chevrons+dot (W-Z)
    'templar': {
        # X wedges (no dot): A-D
        'a': ('x_wedge', 'top', 0), 'b': ('x_wedge', 'right', 0),
        'c': ('x_wedge', 'bottom', 0), 'd': ('x_wedge', 'left', 0),
        # Plus arms (no dot): E-H
        'f': ('plus_arm', 'right', 0), 'g': ('plus_arm', 'bottom', 0),
        'e': ('plus_arm', 'left', 0), 'h': ('plus_arm', 'top', 0),
        # Plus chevrons (no dot): I/J, K, L, M (I and J share same symbol)
        'i': ('plus_chevron', 'top', 0), 'j': ('plus_chevron', 'top', 0),
        'k': ('plus_chevron', 'right', 0), 'l': ('plus_chevron', 'bottom', 0),
        'm': ('plus_chevron', 'left', 0),
        # Full X (no dot): N
        'n': ('full_x', 'center', 0),
        # X wedges (1 dot): O-R
        'o': ('x_wedge', 'top', 1), 'p': ('x_wedge', 'right', 1),
        'q': ('x_wedge', 'bottom', 1), 'r': ('x_wedge', 'left', 1),
        # Plus arms (1 dot): S-V
        's': ('plus_arm', 'top', 1), 't': ('plus_arm', 'right', 1),
        'u': ('plus_arm', 'bottom', 1), 'v': ('plus_arm', 'left', 1),
        # Plus chevrons (1 dot): W-Z
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

    # Draw the edges
    if top:
        draw.line([(x1, y1), (x2, y1)], fill='black', width=LINE_WIDTH)
    if right:
        draw.line([(x2, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
    if bottom:
        draw.line([(x1, y2), (x2, y2)], fill='black', width=LINE_WIDTH)
    if left:
        draw.line([(x1, y1), (x1, y2)], fill='black', width=LINE_WIDTH)

    # Draw dots
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
    """Draw an X-based wedge shape (V, <, >, ^)."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    if direction == 'bottom':
        # V shape pointing up (bottom wedge of X)
        draw.line([(cx, y1), (x1, y2)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy + 3
    elif direction == 'left':
        # < shape pointing right (left wedge of X)
        draw.line([(x2, cy), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x2, cy), (x1, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx - 3, cy
    elif direction == 'top':
        # ^ shape pointing down (top wedge of X)
        draw.line([(cx, y2), (x1, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(cx, y2), (x2, y1)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx, cy - 3
    elif direction == 'right':
        # > shape pointing left (right wedge of X)
        draw.line([(x1, cy), (x2, y1)], fill='black', width=LINE_WIDTH)
        draw.line([(x1, cy), (x2, y2)], fill='black', width=LINE_WIDTH)
        dot_cx, dot_cy = cx + 3, cy

    # Draw dots
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

    # Draw dots
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

    # Draw dots
    if num_dots >= 1:
        draw.ellipse([(dot_cx - DOT_RADIUS, dot_cy - DOT_RADIUS),
                      (dot_cx + DOT_RADIUS, dot_cy + DOT_RADIUS)], fill='black')


def draw_full_x(draw, x, y, direction, num_dots, size=CELL_SIZE):
    """Draw a complete X shape (for Templar N)."""
    margin = 8
    cx, cy = x + size // 2, y + size // 2

    x1, y1 = x + margin, y + margin
    x2, y2 = x + size - margin, y + size - margin

    # Draw both diagonals
    draw.line([(x1, y1), (x2, y2)], fill='black', width=LINE_WIDTH)
    draw.line([(x1, y2), (x2, y1)], fill='black', width=LINE_WIDTH)

    # Draw dots
    if num_dots >= 1:
        draw.ellipse([(cx - DOT_RADIUS, cy - DOT_RADIUS),
                      (cx + DOT_RADIUS, cy + DOT_RADIUS)], fill='black')


def draw_symbol(draw, x, y, symbol_type, direction, num_dots, size=CELL_SIZE):
    """Draw a Pigpen symbol based on its type."""
    if symbol_type == 'grid':
        draw_grid_symbol(draw, x, y, direction, num_dots, size)
    elif symbol_type == 'x_wedge':
        draw_x_wedge(draw, x, y, direction, num_dots, size)
    elif symbol_type == 'plus_arm':
        draw_plus_arm(draw, x, y, direction, num_dots, size)
    elif symbol_type == 'plus_chevron':
        draw_plus_chevron(draw, x, y, direction, num_dots, size)
    elif symbol_type == 'full_x':
        draw_full_x(draw, x, y, direction, num_dots, size)


def encode_message(message, variant):
    """Encode a message using the specified Pigpen variant."""
    mapping = VARIANTS[variant]
    symbols = []

    for char in message.lower():
        if char == ' ':
            symbols.append(('space', None, None, None))
        elif char in mapping:
            symbol_type, direction, num_dots = mapping[char]
            symbols.append(('symbol', symbol_type, direction, num_dots))
        # Skip non-alphabetic characters except spaces

    return symbols


def create_image(symbols, output_file):
    """Create an image from encoded symbols."""
    if not symbols:
        print("Error: No valid symbols to encode.")
        exit(1)

    # Calculate image dimensions
    num_symbols = sum(1 for s in symbols if s[0] == 'symbol')
    num_spaces = sum(1 for s in symbols if s[0] == 'space')

    width = num_symbols * CELL_SIZE + num_spaces * SPACE_WIDTH + 20  # padding
    height = CELL_SIZE + 20  # padding

    # Create image
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)

    # Draw each symbol
    x = 10  # starting x with padding
    y = 10  # starting y with padding

    for entry in symbols:
        if entry[0] == 'space':
            x += SPACE_WIDTH
        else:
            _, symbol_type, direction, num_dots = entry
            draw_symbol(draw, x, y, symbol_type, direction, num_dots)
            x += CELL_SIZE

    img.save(output_file)
    return img


# Process the message
secret_message = args.secret_message
variant = args.variant

# Encode the message
symbols = encode_message(secret_message, variant)

if not symbols:
    print("Error: Message contains no valid characters to encode.")
    exit(1)

# Create and save the image
create_image(symbols, args.output_file)

# Count actual letters encoded
letter_count = sum(1 for s in symbols if s[0] == 'symbol')

print(f"Variant: {variant}")
print(f"Original message: {secret_message}")
print(f"Encrypted message saved to: {args.output_file}")
print(f"Number of symbols: {letter_count}")
