import argparse

parser = argparse.ArgumentParser(
    prog="AlbertiDecipher",
    description="""Decipher script for the Alberti Cipher. Reverses the encryption by using the same disk
    configuration and reversing the character lookups."""
)

parser.add_argument('encrypted_message',
                    type=str,
                    help="Message to decipher")

parser.add_argument('stationary_disk',
                    type=str,
                    help="The stationary disk configuration used during encryption")

parser.add_argument('movable_disk',
                    type=str,
                    help="The movable disk configuration used during encryption (with k at position 0)")

parser.add_argument('-m2', '--method-two',
                    dest="method_two",
                    action="store_true",
                    default=False,
                    help="Use the advanced alberti cipher decoding method")

args = parser.parse_args()

encrypted_message = args.encrypted_message.replace(" ", "")  # Keep original case
stationary_disk = args.stationary_disk
movable_disk = args.movable_disk
method_two = args.method_two

stationary_disk_len = len(stationary_disk)
movable_disk_len = len(movable_disk)

decrypted_message = ""
k_offset = 0
message_index = 0

if method_two and len(encrypted_message) > 0:
    k_offset = movable_disk_len - movable_disk.index(encrypted_message[0])
    message_index += 1

# Process each character in the encrypted message
while message_index < len(encrypted_message):
    current_char = encrypted_message[message_index]

    # Check for rotation indicators
    if method_two:
        movable_index = movable_disk.index(current_char.lower())
        stationary_index = (movable_index + k_offset) % movable_disk_len
        possible_signal_char = stationary_disk[stationary_index]

        # Method 2: Numbers indicate rotation
        if possible_signal_char.isdigit():
            # Rotate so that the letter at digit_value position aligns with index letter (position 0)
            k_offset = movable_disk_len - movable_index
            message_index += 1
            continue
    else:
        # Default method: Capital letters indicate rotation
        if current_char.isupper():
            # Rotate so that 'k' on movable disk aligns with this capital letter on stationary disk
            k_offset = stationary_disk.index(current_char)
            message_index += 1
            continue

    # Convert to lowercase for processing
    encrypted_char = current_char.lower()
    movable_index = movable_disk.index(encrypted_char)
    stationary_index = (movable_index + k_offset) % movable_disk_len

    # Check if this is a doubled character (for h, j, k, u, w, y)
    if message_index + 1 < len(encrypted_message) and encrypted_message[message_index + 1].lower() == encrypted_char:
        doubled_char_found = True

        # This is a doubled character
        base_char = stationary_disk[stationary_index]

        # Map back to the special characters
        if base_char == 'F':
            decrypted_message += 'h'
        elif base_char == 'I':
            decrypted_message += 'j'
        elif base_char == 'Q':
            decrypted_message += 'k'
        elif base_char == 'V':
            decrypted_message += 'u'
        elif base_char == 'X':
            decrypted_message += 'w'
        elif base_char == 'Z':
            decrypted_message += 'y'
        else:
            doubled_char_found = False

        if doubled_char_found:
            # Skip the next character since it's part of this double
            message_index += 2
            continue

    # Regular character - decrypt it
    decrypted_message += stationary_disk[stationary_index].lower()

    message_index += 1

print("Stationary disk: " + stationary_disk)
print("Movable disk:    " + movable_disk)
if method_two:
    print("Index letter: " + stationary_disk[0])
else:
    print("Key letter: k")
print()
print("Encrypted Message: " + args.encrypted_message)
print("Decrypted Message: " + decrypted_message)
