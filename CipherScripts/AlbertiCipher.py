import argparse, random

stationary_disk = "ABCDEFGILMNOPQRSTVXZ1234"
stationary_disk_len = len( stationary_disk )
movable_disk = "klnprtuz&xysomqihfdbaceg"
movable_disk_len = len( movable_disk )

def get_encrypted_letter( char ):
    encrypt_char_index = stationary_disk.index(char.upper()) - k_offset
    if encrypt_char_index < 0:
        encrypt_char_index += movable_disk_len
    return movable_disk[ encrypt_char_index ]


parser = argparse.ArgumentParser(
    prog="AlbertiCipher",
    description="""Created in 1467 by Leon Battista Alberti, the Alberti Cipher features a large stationary disc
    with a smaller rotating disc inside of it. The 'k' on the smaller disk is typically matched to the key letter at the
    start of each segment of the encrypted message, but there are plenty of custom ways you can choose to encode your
    messages. This script features the original easier method, and a more complicated method that is robust to frequency
    analysis"""
)

parser.add_argument('secret_message',
                        type=str,
                        help="Message to encipher")

parser.add_argument('-f', '--frequency',
                        dest="frequency_rotate",
                        default=10,
                        type=int,
                        help="Frequency with which to rotate the disk to a new index. Default = every 10 characters")
parser.add_argument('-m2' '--method-two',
                        dest="method_two",
                        action="store_true",
                        default=False,
                        help="Use the advanced alberti cipher encoding method")

args = parser.parse_args()

secret_message = args.secret_message.replace(" ","").lower()
frequency_rotate = args.frequency_rotate
method_two = args.method_two

encrypted_message = ""

k_offset = 0
iters_until_rotate = 0

if method_two:
    k_offset = random.randrange( 0, stationary_disk_len )
    iters_until_rotate = frequency_rotate
    encrypted_message += movable_disk[ movable_disk_len - k_offset ]

for char in secret_message:
    if iters_until_rotate == 0:
        iters_until_rotate = frequency_rotate

        if method_two:
            next_num = str( random.randrange( 1, 5 ) )
            new_key = stationary_disk.index( next_num )
            encrypted_message +=  movable_disk[ new_key ]
            k_offset = movable_disk_len - new_key
        else:
            k_offset = random.randrange( 0, stationary_disk_len )
            encrypted_message += stationary_disk[ k_offset ]
    
    # Workaround for characters that were not in the original alberti cipher disks
    if char == 'h':
        encrypted_message += get_encrypted_letter( 'f' ) * 2
    elif char == 'j':
        encrypted_message += get_encrypted_letter( 'i' ) * 2
    elif char == 'k':
        encrypted_message += get_encrypted_letter( 'q' ) * 2
    elif char == 'u':
        encrypted_message += get_encrypted_letter( 'v' ) * 2
    elif char == 'w':
        encrypted_message += get_encrypted_letter( 'x' ) * 2
    elif char == 'y':
        encrypted_message += get_encrypted_letter( 'z' ) * 2
    else:
        encrypted_message += get_encrypted_letter( char )

    iters_until_rotate -= 1

print( "Stationary disk: "  + stationary_disk )
print( "Movable disk: " + movable_disk )
print()
print( "Original Message: " + secret_message )
print( "Encrypted Message: " + encrypted_message )