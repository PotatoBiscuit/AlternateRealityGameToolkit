#!/usr/bin/env python3
"""
Bacon's Cipher - A steganographic cipher that hides messages using binary encoding.

Created by Francis Bacon in 1605, this cipher encodes each letter as a 5-bit binary sequence.
The binary sequence can then be hidden in various ways, such as through typography (capitalization),
raw binary representation, or using Unicode lookalike characters.
"""

import argparse
import random
import string

# 24-letter Bacon cipher (I/J combined, U/V combined)
BACON_24 = {
    'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
    'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAA',
    'K': 'ABAAB', 'L': 'ABABA', 'M': 'ABABB', 'N': 'ABBAA', 'O': 'ABBAB',
    'P': 'ABBBA', 'Q': 'ABBBB', 'R': 'BAAAA', 'S': 'BAAAB', 'T': 'BAABA',
    'U': 'BAABB', 'V': 'BAABB', 'W': 'BABAA', 'X': 'BABAB', 'Y': 'BABBA',
    'Z': 'BABBB'
}

# 26-letter Bacon cipher (all letters unique)
BACON_26 = {
    'A': 'AAAAA', 'B': 'AAAAB', 'C': 'AAABA', 'D': 'AAABB', 'E': 'AABAA',
    'F': 'AABAB', 'G': 'AABBA', 'H': 'AABBB', 'I': 'ABAAA', 'J': 'ABAAB',
    'K': 'ABABA', 'L': 'ABABB', 'M': 'ABBAA', 'N': 'ABBAB', 'O': 'ABBBA',
    'P': 'ABBBB', 'Q': 'BAAAA', 'R': 'BAAAB', 'S': 'BAABA', 'T': 'BAABB',
    'U': 'BABAA', 'V': 'BABAB', 'W': 'BABBA', 'X': 'BABBB', 'Y': 'BBAAA',
    'Z': 'BBAAB'
}

# Unicode lookalikes - pairs of visually similar characters from different scripts
# Format: (character for 'A'/0, character for 'B'/1)
LOOKALIKE_PAIRS = [
    ('a', '\u0430'),  # Latin 'a' vs Cyrillic 'а'
    ('e', '\u0435'),  # Latin 'e' vs Cyrillic 'е'
    ('o', '\u043e'),  # Latin 'o' vs Cyrillic 'о'
    ('p', '\u0440'),  # Latin 'p' vs Cyrillic 'р'
    ('c', '\u0441'),  # Latin 'c' vs Cyrillic 'с'
    ('x', '\u0445'),  # Latin 'x' vs Cyrillic 'х'
    ('y', '\u0443'),  # Latin 'y' vs Cyrillic 'у'
    ('i', '\u0456'),  # Latin 'i' vs Cyrillic 'і'
    ('s', '\u0455'),  # Latin 's' vs Cyrillic 'ѕ'
    ('j', '\u0458'),  # Latin 'j' vs Cyrillic 'ј'
]


def encode_to_bacon(message, variant):
    """Encode message to Bacon cipher binary string."""
    cipher_dict = BACON_26 if variant == 26 else BACON_24
    message = message.upper().replace(" ", "")

    bacon_code = ""
    for char in message:
        if char.isalpha():
            bacon_code += cipher_dict[char]

    return bacon_code


def bacon_to_capitalization(bacon_code, cover_text):
    """
    Encode Bacon cipher as capitalization in cover text.
    A = lowercase, B = uppercase
    """
    # Remove non-alphabetic characters from cover text to check if enough capitalizable chars are in cover text
    cover_letters = [c for c in cover_text if c.isalpha()]

    # Check if we need more letters
    needed_letters = len(bacon_code)
    if len(cover_letters) < needed_letters:
        # Generate random filler text
        additional_needed = needed_letters - len(cover_letters)
        filler = ''.join(random.choices(string.ascii_lowercase, k=additional_needed))
        cover_letters.extend(list(filler))
        print(f"Note: Cover text was too short. Added {additional_needed} random letters as filler.\n")

    # Build the encoded message
    result = []
    cover_idx = 0
    original_idx = 0

    for char in cover_text:
        if char.isalpha() and cover_idx < len(bacon_code):
            # Use the bacon code to determine case
            if bacon_code[cover_idx] == 'A':
                result.append(char.lower())
            else:  # 'B'
                result.append(char.upper())
            cover_idx += 1
        else:
            result.append(char)
        original_idx += 1

    # Add any remaining encoded characters (filler)
    while cover_idx < len(bacon_code):
        if bacon_code[cover_idx] == 'A':
            result.append(cover_letters[cover_idx].lower())
        else:
            result.append(cover_letters[cover_idx].upper())
        cover_idx += 1

    return ''.join(result)


def bacon_to_binary(bacon_code):
    """Convert Bacon cipher to raw binary (A=0, B=1)."""
    return bacon_code.replace('A', '0').replace('B', '1')


def bacon_to_unicode(bacon_code):
    """
    Encode Bacon cipher using Unicode lookalike characters.
    Randomly selects from different lookalike pairs to make detection harder.
    A = Latin character, B = Cyrillic lookalike
    """
    result = []
    for bit in bacon_code:
        # Randomly select a lookalike pair for variety
        pair = random.choice(LOOKALIKE_PAIRS)
        if bit == 'A':
            result.append(pair[0])  # Latin
        else:  # 'B'
            result.append(pair[1])  # Cyrillic

    return ''.join(result)


def main():
    parser = argparse.ArgumentParser(
        prog="BaconCipher",
        description="""Bacon's Cipher - A steganographic cipher invented by Francis Bacon in 1605.
        Encodes messages as 5-bit binary sequences that can be hidden using capitalization,
        raw binary, or Unicode lookalike characters. Supports both 24-letter (I/J and U/V combined)
        and 26-letter (all unique) variants."""
    )

    parser.add_argument('secret_message',
                        type=str,
                        help="Message to encode with Bacon cipher")

    parser.add_argument('--mode',
                        type=str,
                        choices=['capitalization', 'binary', 'unicode'],
                        default='capitalization',
                        help="Encoding mode: 'capitalization' (hide in cover text), 'binary' (raw 0s and 1s), or 'unicode' (lookalike characters)")

    parser.add_argument('--cover-text',
                        type=str,
                        help="Cover text for capitalization mode (required if mode=capitalization)")

    parser.add_argument('--variant',
                        type=int,
                        choices=[24, 26],
                        default=24,
                        help="Bacon cipher variant: 24 (I/J and U/V combined) or 26 (all letters unique)")

    args = parser.parse_args()

    # Validate arguments
    if args.mode == 'capitalization' and not args.cover_text:
        parser.error("--cover-text is required when using capitalization mode")

    # Encode the message
    bacon_code = encode_to_bacon(args.secret_message, args.variant)

    print(f"Secret Message: {args.secret_message.upper().replace(' ', '')}")
    print(f"Variant: {args.variant}-letter")
    print(f"Mode: {args.mode}")
    print()

    # Generate output based on mode
    if args.mode == 'capitalization':
        encoded = bacon_to_capitalization(bacon_code, args.cover_text)
        print(f"Cover Text: {args.cover_text}")
        print(f"Encoded Message:\n{encoded}")

    elif args.mode == 'binary':
        encoded = bacon_to_binary(bacon_code)
        print(f"Binary Encoding:\n{encoded}")

    elif args.mode == 'unicode':
        encoded = bacon_to_unicode(bacon_code)
        print(f"Unicode Encoding:\n{encoded}")
        print(f"\nNote: This text uses a mix of Latin and Cyrillic lookalike characters.")
        print(f"It may appear as normal text but encodes your secret message.")

    return 0


if __name__ == "__main__":
    exit(main())
