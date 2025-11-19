#!/usr/bin/env python3
"""
Bacon's Cipher Decipher - Decodes messages hidden using Bacon's cipher.

Supports decoding from capitalization patterns, raw binary, or Unicode lookalike characters.
"""

import argparse
import unicodedata

# 24-letter Bacon cipher (I/J combined, U/V combined)
BACON_24_DECODE = {
    'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D', 'AABAA': 'E',
    'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H', 'ABAAA': 'I', 'ABAAB': 'K',
    'ABABA': 'L', 'ABABB': 'M', 'ABBAA': 'N', 'ABBAB': 'O', 'ABBBA': 'P',
    'ABBBB': 'Q', 'BAAAA': 'R', 'BAAAB': 'S', 'BAABA': 'T', 'BAABB': 'U',
    'BABAA': 'W', 'BABAB': 'X', 'BABBA': 'Y', 'BABBB': 'Z'
}

# 26-letter Bacon cipher (all letters unique)
BACON_26_DECODE = {
    'AAAAA': 'A', 'AAAAB': 'B', 'AAABA': 'C', 'AAABB': 'D', 'AABAA': 'E',
    'AABAB': 'F', 'AABBA': 'G', 'AABBB': 'H', 'ABAAA': 'I', 'ABAAB': 'J',
    'ABABA': 'K', 'ABABB': 'L', 'ABBAA': 'M', 'ABBAB': 'N', 'ABBBA': 'O',
    'ABBBB': 'P', 'BAAAA': 'Q', 'BAAAB': 'R', 'BAABA': 'S', 'BAABB': 'T',
    'BABAA': 'U', 'BABAB': 'V', 'BABBA': 'W', 'BABBB': 'X', 'BBAAA': 'Y',
    'BBAAB': 'Z'
}


def is_cyrillic(char):
    """Check if a character is from the Cyrillic script."""
    try:
        return unicodedata.name(char).startswith('CYRILLIC')
    except ValueError:
        return False


def is_latin(char):
    """Check if a character is from the Latin script."""
    try:
        name = unicodedata.name(char)
        return name.startswith('LATIN') or (char.isalpha() and ord(char) < 128)
    except ValueError:
        return False


def extract_bacon_from_capitalization(text):
    """
    Extract Bacon code from capitalization pattern.
    lowercase = A, uppercase = B
    """
    bacon_code = ""
    for char in text:
        if char.isalpha():
            if char.islower():
                bacon_code += 'A'
            else:
                bacon_code += 'B'

    return bacon_code


def extract_bacon_from_binary(text):
    """
    Extract Bacon code from binary string.
    0 = A, 1 = B
    """
    # Remove any whitespace
    text = text.replace(' ', '').replace('\n', '').replace('\r', '')

    # Convert binary to Bacon code
    bacon_code = text.replace('0', 'A').replace('1', 'B')

    return bacon_code


def extract_bacon_from_unicode(text):
    """
    Extract Bacon code from Unicode lookalike characters.
    Latin = A, Cyrillic = B
    """
    bacon_code = ""
    for char in text:
        if is_latin(char):
            bacon_code += 'A'
        elif is_cyrillic(char):
            bacon_code += 'B'
        # Ignore other characters

    return bacon_code


def decode_bacon(bacon_code, variant):
    """Decode Bacon cipher binary string to plaintext."""
    decode_dict = BACON_26_DECODE if variant == 26 else BACON_24_DECODE

    # Split into 5-character chunks
    decoded_message = ""
    for i in range(0, len(bacon_code), 5):
        chunk = bacon_code[i:i+5]
        if len(chunk) == 5:
            if chunk in decode_dict:
                decoded_message += decode_dict[chunk]
            else:
                decoded_message += '?'  # Unknown code

    return decoded_message


def main():
    parser = argparse.ArgumentParser(
        prog="BaconDecipher",
        description="""Bacon's Cipher Decipher - Decodes messages hidden using Bacon's cipher.
        Supports decoding from capitalization patterns, raw binary (0s and 1s),
        or Unicode lookalike characters. Must specify the encoding mode used."""
    )

    parser.add_argument('encrypted_message',
                        type=str,
                        help="Encoded message to decipher")

    parser.add_argument('--mode',
                        type=str,
                        choices=['capitalization', 'binary', 'unicode'],
                        required=True,
                        help="Encoding mode used: 'capitalization', 'binary', or 'unicode'")

    parser.add_argument('--variant',
                        type=int,
                        choices=[24, 26],
                        default=24,
                        help="Bacon cipher variant: 24 (I/J and U/V combined) or 26 (all letters unique)")

    args = parser.parse_args()

    # Extract Bacon code based on mode
    if args.mode == 'capitalization':
        bacon_code = extract_bacon_from_capitalization(args.encrypted_message)
        print(f"Mode: Capitalization")
        print(f"Encrypted Text: {args.encrypted_message}")

    elif args.mode == 'binary':
        bacon_code = extract_bacon_from_binary(args.encrypted_message)
        print(f"Mode: Binary")
        print(f"Binary Input: {args.encrypted_message}")

    elif args.mode == 'unicode':
        bacon_code = extract_bacon_from_unicode(args.encrypted_message)
        print(f"Mode: Unicode lookalikes")
        print(f"Encoded Text: {args.encrypted_message}")

    print(f"Variant: {args.variant}-letter")
    print(f"Extracted Bacon Code: {bacon_code}")
    print()

    # Decode the Bacon code
    decoded_message = decode_bacon(bacon_code, args.variant)

    print(f"Decrypted Message: {decoded_message}")

    # Warn if there were any unknown codes
    if '?' in decoded_message:
        print("\nWarning: Some codes could not be decoded (marked with '?').")
        print("This may indicate an incorrect variant or corrupted input.")

    return 0


if __name__ == "__main__":
    exit(main())
