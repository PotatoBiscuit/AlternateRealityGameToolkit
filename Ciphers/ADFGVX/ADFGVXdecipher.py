import argparse, collections, sys, csv

def find_polybius_char(matrix, character, size=6):
    for p in range(size):
        for k in range(size):
            if character in polybius_matrix[p][k]:
                return p, k

# Start out with arrays suited for a small polybius square (ADFGX)
polybius_matrix_size = 5
polybius_label = ["A", "D", "F", "G", "X"]
alphabet = ["a", "b", "c", "d", "e", "f", "g", "h", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "i/j"]

parser = argparse.ArgumentParser(
    prog='ADFGVXdecipher',
    description="""Decipher script for the ADFGVX cipher used by the Imperial German Army during World War I.
    Reverses the columnar transposition and Polybius square substitution."""
)
parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher (space-separated columns)")
parser.add_argument('transposition_key',
                    type=str,
                    help="The keyword used for columnar transposition")
parser.add_argument('polybius_square_file',
                    type=str,
                    help="Path to CSV file containing the Polybius square")
parser.add_argument('-p', '--polybius-size',
                    dest='polybius_size',
                    type=str,
                    default="big",
                    required=False,
                    help="Default is 'big', small/big only. Associated with ADFGX/ADFGVX ciphers respectively")
args = parser.parse_args()

# If small polybius square isn't specified, prepare for the big one (ADFGVX)
if args.polybius_size != "small":
    polybius_label = polybius_label[:-1] + ["V"] + [polybius_label[-1]]
    polybius_matrix_size = 6

encrypted_message = args.encrypted_message.replace(" ", "").upper()
transposition_key = args.transposition_key.replace(" ", "").lower()

# Read the polybius matrix from the CSV file
polybius_matrix = []
try:
    with open(args.polybius_square_file, 'r') as csvfile:
        csv_reader = csv.reader(csvfile)
        for row in csv_reader:
            polybius_matrix.append([cell.strip().lower() for cell in row])
except FileNotFoundError:
    print(f"Error: Could not find file '{args.polybius_square_file}'")
    sys.exit(1)
except Exception as e:
    print(f"Error reading CSV file: {e}")
    sys.exit(1)

# Validate the polybius matrix size
if len(polybius_matrix) != polybius_matrix_size:
    print(f"Error: Polybius square must have {polybius_matrix_size} rows, but got {len(polybius_matrix)}")
    print(f"Make sure to specify '-p small' if you are using the smaller 5x5 polybius square format")
    sys.exit(1)
for i, row in enumerate(polybius_matrix):
    if len(row) != polybius_matrix_size:
        print(f"Error: Row {i} must have {polybius_matrix_size} columns, but got {len(row)}")
        print(f"Make sure to specify '-p small' if you are using the smaller 5x5 polybius square format")
        sys.exit(1)

# Split the encrypted message into columns (they come space-separated)
columns = args.encrypted_message.split()
transposition_key_len = len(transposition_key)

# Figure out the original column order by sorting the transposition key
index_dict = {}
for i in range(transposition_key_len):
    if transposition_key[i] in index_dict:
        print("Error: Transposition key must be all unique characters")
        sys.exit()
    index_dict[transposition_key[i]] = i

sorted_indices = collections.OrderedDict(sorted(index_dict.items()))

# Map sorted columns back to original positions
original_columns = [""]*transposition_key_len
col_idx = 0
for _, original_index in sorted_indices.items():
    original_columns[original_index] = columns[col_idx]
    col_idx += 1

# Read left->right, top->bottom to get intermediate cipher text
intermediate = ""
for i in range(len(original_columns)):
    for j in range(len(original_columns)):
        if( i < len(original_columns[j])):
            intermediate += original_columns[j][i]

# Now decode from polybius coordinates
decrypted_message = ""
for i in range(0, len(intermediate), 2):
    row_char = intermediate[i]
    col_char = intermediate[i+1]

    row = polybius_label.index(row_char)
    col = polybius_label.index(col_char)

    decrypted_message += polybius_matrix[row][col]

print("Polybius square used:")
print("   " + "   ".join(polybius_label))
for i in range(len(polybius_matrix)):
    print_text = polybius_label[i] + "  "
    for j in range(len(polybius_matrix[i])):
        print_text += polybius_matrix[i][j] + " "
        if polybius_matrix[i][j] != "i/j":
            print_text += "  "
    print(print_text)

print()
print("Transposition key: " + transposition_key)
print("Encrypted message: " + args.encrypted_message)
print("Decrypted message: " + decrypted_message)
