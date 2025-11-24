import argparse

parser = argparse.ArgumentParser(
    prog="ChaocipherCipher",
    description="""The Chaocipher is a cipher featuring dynamic substitution, invented by John F. Byrne in 1918.
    It uses two dynamically permuted alphabets that change after each character is encrypted,
    making it resistant to traditional cryptanalysis methods. The algorithm remained secret
    until 2010 when Byrne's family donated his papers to the National Cryptologic Museum."""
)

parser.add_argument('secret_message',
                    type=str,
                    help="Message to encipher")

parser.add_argument('-l', '--left',
                    dest="left_alphabet",
                    required=True,
                    type=str,
                    help="Left (ciphertext) alphabet - 26 unique letters. Starts at zenith, in order counterclockwise")

parser.add_argument('-r', '--right',
                    dest="right_alphabet",
                    required=True,
                    type=str,
                    help="Right (plaintext) alphabet - 26 unique letters. Starts at zenith, in order clockwise")

args = parser.parse_args()


def validate_alphabet(alphabet, name):
    """Validate that an alphabet contains exactly 26 unique letters."""
    alphabet = alphabet.upper()
    if len(alphabet) != 26:
        raise ValueError(f"{name} alphabet must contain exactly 26 characters, got {len(alphabet)}")
    if len(set(alphabet)) != 26:
        raise ValueError(f"{name} alphabet must contain 26 unique characters")
    if not alphabet.isalpha():
        raise ValueError(f"{name} alphabet must contain only letters")
    return alphabet


def permute_left(alphabet, index):
    """Permute the left (ciphertext) alphabet after encryption."""
    # Step 1: Rotate so the ciphertext character is at position 0 (zenith)
    alphabet = alphabet[index:] + alphabet[:index]

    # Step 2: Extract character at index 1, shift indices 2-13 left, insert at index 13
    extracted = alphabet[1]
    alphabet = alphabet[0] + alphabet[2:14] + extracted + alphabet[14:]

    return alphabet


def permute_right(alphabet, index):
    """Permute the right (plaintext) alphabet after encryption."""
    # Step 1: Rotate so the plaintext character is at position 0
    alphabet = alphabet[index:] + alphabet[:index]

    # Step 2: Rotate one more position to the left
    alphabet = alphabet[1:] + alphabet[0]

    # Step 3: Extract character at index 2, shift indices 3-13 left, insert at index 13
    extracted = alphabet[2]
    alphabet = alphabet[:2] + alphabet[3:14] + extracted + alphabet[14:]

    return alphabet


def chaocipher_encrypt(plaintext, left_alphabet, right_alphabet):
    """Encrypt plaintext using the Chaocipher algorithm."""
    ciphertext = ""

    for char in plaintext:
        if char.upper().isalpha():
            was_lower = char.islower()
            char_upper = char.upper()

            # Find position of plaintext character in right alphabet
            index = right_alphabet.index(char_upper)

            # Get ciphertext character from left alphabet at same position
            cipher_char = left_alphabet[index]

            # Preserve case
            if was_lower:
                cipher_char = cipher_char.lower()
            ciphertext += cipher_char

            # Permute both alphabets
            left_alphabet = permute_left(left_alphabet, index)
            right_alphabet = permute_right(right_alphabet, index)
        else:
            # Non-alphabetic characters pass through unchanged
            ciphertext += char

    return ciphertext


# Validate and normalize alphabets
left_alphabet = validate_alphabet(args.left_alphabet, "Left")
right_alphabet = validate_alphabet(args.right_alphabet, "Right")

secret_message = args.secret_message
encrypted_message = chaocipher_encrypt(secret_message, left_alphabet, right_alphabet)

print("Left Alphabet: " + args.left_alphabet.upper())
print("Right Alphabet: " + args.right_alphabet.upper())
print()
print("Original message: " + secret_message)
print("Encrypted message: " + encrypted_message)
