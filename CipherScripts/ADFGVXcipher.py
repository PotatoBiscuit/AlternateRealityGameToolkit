import argparse, collections, random, sys

def find_polybius_char( matrix, character, size=6 ):
    for p in range( size ):
        for k in range( size ):
            if character in polybius_matrix[p][k]:
                return p,k

# Start out with arrays suited for a small polybius square (ADFGX)
polybius_matrix_size = 5
polybius_label = ["A","D","F","G","X"]
alphabet = ["a","b","c","d","e","f","g","h","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z","i/j"]

parser = argparse.ArgumentParser(
    prog='ADFGVXcipher',
    description="""Cipher used by the Imperial German Army during World War I. Invented by German Lieutenant Fritz Nebel, it
    uses a modified Polybius square and does columnar transposition. Eventually cracked by French Lieutenant Georges Painvin."""
)
parser.add_argument('secret_message',
                        type=str,
                        required=True,
                        help="Message to encipher")
parser.add_argument('transposition_key',
                        type=str,
                        required=True,
                        help="Determines the keyword to perform columnar transposition. MUST have unique characters")
parser.add_argument('-p','--polybius-size',
                        dest='polybius_size',
                        type=str,
                        default="big",
                        required=False,
                        help="Default is 'big', small/big only. Associated with ADFGX/ADFGVX ciphers respectively")
args = parser.parse_args()

# If small polybius square isn't specified, prepare for the big one (ADFGVX)
if args.polybius_size != "small":
    polybius_label = polybius_label[:-1] + ["V"] + [polybius_label[-1]]
    alphabet = alphabet[:-1] + ["i", "j", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    polybius_matrix_size = 6

secret_message = args.secret_message.replace(" ","").lower()
transposition_key = args.transposition_key.replace(" ","").lower()

# Shuffle letter order for making a randomized polybius square
random.shuffle( alphabet )
polybius_matrix = [ [""]*polybius_matrix_size for i in range(polybius_matrix_size) ]

# Assigned shuffled letters to polybius square
for i in range( polybius_matrix_size ):
    for j in range( polybius_matrix_size ):
        polybius_matrix[i][j] = alphabet[ i*polybius_matrix_size + j ]

# Match message to polybius square for step 1 of encryption
transposition_key_len = len( transposition_key )
secret_message_len = len( secret_message )
ciphered_stage1_matrix = [ [] for letter in transposition_key ]
row = 0
for i in range( secret_message_len ):
    p,k = find_polybius_char( polybius_matrix, secret_message[i], polybius_matrix_size )
    ciphered_stage1_matrix[ row ].append( polybius_label[p] )
    row = ( row + 1 ) % transposition_key_len
    ciphered_stage1_matrix[ row ].append( polybius_label[k] )
    row = ( row + 1 ) % transposition_key_len

# Figure out how the row-wise transposition should take place by assigning
# indices to dict and sorting based on characters in transposition key.
# Rows are used instead of columns here because it is easier to work with in code,
# but it is functionally the same.
index_dict = {}
for i in range( transposition_key_len ):
    if transposition_key[i] in index_dict:
        print("Error: Transposition key must be all unique characters")
        sys.exit()
    index_dict[ transposition_key[i] ] = i

sorted_indices = collections.OrderedDict( sorted( index_dict.items() ) )
transposition_matrix = [""]*transposition_key_len

# Perform transposition, and put characters into a cleaner format
row = 0
for _, new_index in sorted_indices.items():
    transposition_matrix[row] = "".join( ciphered_stage1_matrix[new_index] )
    row += 1

# Get ciphertext as a single string
ciphertext = " ".join( transposition_matrix )

print( "Polybius square used:" )
print( "   " + "   ".join( polybius_label ) )
for i in range( len(polybius_matrix ) ):
    print_text = polybius_label[i] + "  "
    for j in range( len(polybius_matrix[i] ) ):
        print_text += polybius_matrix[i][j] + " "
        if polybius_matrix[i][j] != "i/j":
            print_text += "  "
    print( print_text )

print()
print( "Transposition key: " + transposition_key )

print( "Original message:  " + secret_message )
print( "Encrypted message: " + ciphertext )