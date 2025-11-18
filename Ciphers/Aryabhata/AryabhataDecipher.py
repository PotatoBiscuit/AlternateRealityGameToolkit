#!/usr/bin/env python3
"""
Aryabhata Decipher - Converts Sanskrit syllables back to numbers using Aryabhata's numeral system.

The Aryabhata numeral system is additive: syllables combine to form the total number.
For example: kuchi = ku + chi = (1×10000) + (6×100) = 10,600
Note: Numerals are written smallest to largest from left to right, but since the system
is additive, the order doesn't affect the final value.
"""

import argparse
import unicodedata

# Consonant base values (reverse mapping)
CONSONANTS = {
    'क': 1,   # ka
    'ख': 2,   # kha
    'ग': 3,   # ga
    'घ': 4,   # gha
    'ङ': 5,   # ṅa
    'च': 6,   # ca
    'छ': 7,   # cha
    'ज': 8,   # ja
    'झ': 9,   # jha
    'ञ': 10,  # ña
    'ट': 11,  # ṭa
    'ठ': 12,  # ṭha
    'ड': 13,  # ḍa
    'ढ': 14,  # ḍha
    'ण': 15,  # ṇa
    'त': 16,  # ta
    'थ': 17,  # tha
    'द': 18,  # da
    'ध': 19,  # dha
    'न': 20,  # na
    'प': 21,  # pa
    'फ': 22,  # pha
    'ब': 23,  # ba
    'भ': 24,  # bha
    'म': 25,  # ma
    'य': 30,  # ya
    'र': 40,  # ra
    'ल': 50,  # la
    'व': 60,  # va
    'श': 70,  # śa
    'ष': 80,  # ṣa
    'स': 90,  # sa
    'ह': 100, # ha
}

# Vowel diacritic marks to multipliers
# Note: In Devanagari, consonants have inherent 'a' sound
VOWEL_MARKS = {
    '': 1,              # a (inherent, no mark)
    'ि': 100,           # i
    'ु': 10000,         # u
    'ृ': 1000000,       # ṛ
    'ॢ': 100000000,     # ḷ
    'े': 10000000000,               # e (10^10)
    'ै': 1000000000000,             # ai (10^12)
    'ो': 100000000000000,           # o (10^14)
    'ौ': 10000000000000000,         # au (10^16)
}

# Unicode categories for Devanagari vowel marks
VOWEL_MARK_CATEGORIES = {'Mn', 'Mc'}  # Nonspacing Mark, Spacing Mark

DEVANAGARI_ZERO = '०'


def parse_syllables(text):
    """
    Parse Devanagari text into syllables (consonant + optional vowel mark).

    Returns:
        List of tuples (consonant, vowel_mark)
    """
    syllables = []
    i = 0

    while i < len(text):
        char = text[i]

        # Handle Devanagari zero
        if char == DEVANAGARI_ZERO:
            return [(DEVANAGARI_ZERO, '')]

        # Check if it's a consonant
        if char in CONSONANTS:
            consonant = char
            vowel_mark = ''

            # Check for following vowel marks
            i += 1
            while i < len(text):
                next_char = text[i]
                category = unicodedata.category(next_char)

                # If it's a vowel mark, add it
                if category in VOWEL_MARK_CATEGORIES and next_char in VOWEL_MARKS:
                    vowel_mark += next_char
                    i += 1
                else:
                    break

            syllables.append((consonant, vowel_mark))
        else:
            # Unknown character, skip it
            i += 1

    return syllables


def aryabhata_to_number(text):
    """
    Convert Aryabhata numeral representation back to a number.

    Args:
        text: String of Sanskrit syllables

    Returns:
        Integer value
    """
    if not text:
        return 0

    # Handle Devanagari zero
    if text == DEVANAGARI_ZERO:
        return 0

    # Parse into syllables
    syllables = parse_syllables(text)

    if not syllables:
        return 0

    # Special case: just zero
    if syllables == [(DEVANAGARI_ZERO, '')]:
        return 0

    # Calculate total by adding all syllable values
    total = 0

    for consonant, vowel_mark in syllables:
        if consonant == DEVANAGARI_ZERO:
            continue

        if consonant not in CONSONANTS:
            raise ValueError(f"Unknown consonant: {consonant}")

        consonant_value = CONSONANTS[consonant]

        # Get vowel multiplier (default to 1 for inherent 'a')
        vowel_multiplier = VOWEL_MARKS.get(vowel_mark, 1)

        syllable_value = consonant_value * vowel_multiplier
        total += syllable_value

    return total


def main():
    parser = argparse.ArgumentParser(
        prog="AryabhataDecipher",
        description="""Converts Sanskrit syllables back to numbers using Aryabhata's numeral system.
        The Aryabhata numeral system is additive: syllables combine to form the total number.
        Numerals are written smallest to largest from left to right, but since the system is additive,
        the order doesn't affect the final value."""
    )

    parser.add_argument('aryabhata_text',
                        type=str,
                        help="Sanskrit text to decipher (e.g., कुचि)")

    args = parser.parse_args()

    try:
        number = aryabhata_to_number(args.aryabhata_text)
        print(f"Aryabhata: {args.aryabhata_text}")
        print(f"Number: {number}")
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
