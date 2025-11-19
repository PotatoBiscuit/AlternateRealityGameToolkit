import argparse

def detect_hebrew(message):
    """
    Detect if the message contains Hebrew characters.
    """
    hebrew_start = 0x05D0  # א (aleph)
    hebrew_end = 0x05EA    # ת (tav)

    for char in message:
        char_code = ord(char)
        if hebrew_start <= char_code <= hebrew_end:
            return True
    return False

def atbash_cipher(message, hebrew=False):
    """
    Apply Atbash cipher to the message.
    For alphabet: A↔Z, B↔Y, C↔X, etc.
    For Hebrew: א↔ת, ב↔ש, ג↔ר, etc.
    """
    result = ""

    if hebrew:
        # Hebrew alphabet: aleph (0x05D0) to tav (0x05EA)
        hebrew_start = 0x05D0  # א (aleph)
        hebrew_end = 0x05EA    # ת (tav)
        hebrew_sum = hebrew_start + hebrew_end

        for char in message:
            char_code = ord(char)
            # Check if character is in Hebrew alphabet range
            if hebrew_start <= char_code <= hebrew_end:
                result += chr(hebrew_sum - char_code)
            else:
                result += char
    else:
        # English alphabet
        for char in message:
            if char.isupper():
                # Uppercase A-Z
                result += chr(ord('A') + ord('Z') - ord(char))
            elif char.islower():
                # Lowercase a-z
                result += chr(ord('a') + ord('z') - ord(char))
            else:
                # Non-alphabetic characters remain unchanged
                result += char

    return result

parser = argparse.ArgumentParser(
    prog="AtbashCipher",
    description="""Atbash cipher - reverses the alphabet (A↔Z, B↔Y, etc.). Automatically detects Hebrew or Latin alphabet.
    The name Atbash comes from the first, last, second, and second to last Hebrew Letters \u05d0(Aleph) \u05ea(Taw) \u05d1(Bet) \u05e9(Shin).
    The bible occasionally makes use of this cipher to embed hidden meanings, and it's also found use in Jewish mysticism and
    Kabbalah.
    This cipher is involutory, so you can run this script again on the output to get the original message"""
)

parser.add_argument('message',
                    type=str,
                    help="Message to encipher")

args = parser.parse_args()

message = args.message
is_hebrew = detect_hebrew(message)
encrypted_message = atbash_cipher(message, is_hebrew)

alphabet_type = "Hebrew" if is_hebrew else "English"

print(f"Alphabet: {alphabet_type}")
print()
print("Original message: " + message)
print("Encrypted message: " + encrypted_message)
