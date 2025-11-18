#!/usr/bin/env python3
"""
Aryabhata Cipher - Converts numbers to Sanskrit syllables using Aryabhata's numeral system.

The Aryabhata numeral system is an ancient Indian alphasyllabic numeral system created by
mathematician Aryabhata (476-550 CE). It uses Sanskrit consonants combined with vowel marks
to represent numbers from 1 to 10^18.

System:
- Consonants have base values (ka=1 to ma=25, ya=30, ra=40... ha=100)
- Vowels multiply the consonant value by powers of 10 (a=1, i=100, u=10000, etc.)
- Multiple syllables add together: kuchi = ku + chi = 10000 + 600 = 10600
- Numerals are written smallest to largest from left to right
"""

import argparse
from unicodedata import normalize

# Varga consonants (1-25) - used primarily for values 1-25
VARGA_CONSONANTS = {
    1: '\u0915',   # ka
    2: '\u0916',   # kha
    3: '\u0917',   # ga
    4: '\u0918',   # gha
    5: '\u0919',   # ṅa
    6: '\u091a',   # ca
    7: '\u091b',   # cha
    8: '\u091c',   # ja
    9: '\u091d',   # jha
    10: '\u091e',  # ña
    11: '\u091f',  # ṭa
    12: '\u0920',  # ṭha
    13: '\u0921',  # ḍa
    14: '\u0922',  # ḍha
    15: '\u0923',  # ṇa
    16: '\u0924',  # ta
    17: '\u0925',  # tha
    18: '\u0926',  # da
    19: '\u0927',  # dha
    20: '\u0928',  # na
    21: '\u092a',  # pa
    22: '\u092b',  # pha
    23: '\u092c',  # ba
    24: '\u092d',  # bha
    25: '\u092e',  # ma
}

# Avarga consonants (30, 40, 50, 60, 70, 80, 90, 100) - used for multiples of 10
AVARGA_CONSONANTS = {
    30: '\u092f',  # ya
    40: '\u0930',  # ra
    50: '\u0932',  # la
    60: '\u0935',  # va
    70: '\u0936',  # śa
    80: '\u0937',  # ṣa
    90: '\u0938',  # sa
    100: '\u0939', # ha
}

# Vowel marks (represented as diacritics in Devanagari)
# These multiply the consonant value
VOWELS = {
    1: '',             # a (inherent vowel, no mark needed)
    100: '\u093f',     # i
    10000: '\u0941',   # u
    1000000: '\u0943', # ṛ
    100000000: '\u0962',  # ḷ
    10000000000: '\u0947',                # e (10^10)
    1000000000000: '\u0948',              # ai (10^12)
    100000000000000: '\u094b',            # o (10^14)
    10000000000000000: '\u094c',          # au (10^16)
}

# For zero
DEVANAGARI_ZERO = '\u0966'

def add_syllable(consonant, vowel_power, syllables):
    vowel_mark = VOWELS[vowel_power]
    syllable = "";
    if vowel_power == 100:
        syllable = normalize("NFKD", vowel_mark + consonant)
    else:
        syllable = normalize("NFKD", consonant + vowel_mark)
    syllables.append( syllable )

def number_to_aryabhata(number):
    """
    Convert a number to Aryabhata numeral representation.

    Args:
        number: Integer to convert (0 to 10^18)

    Returns:
        String of Sanskrit syllables representing the number
    """
    if number == 0:
        return DEVANAGARI_ZERO

    if number < 0:
        raise ValueError("Negative numbers are not supported in Aryabhata numerals")

    if number > 10**18:
        raise ValueError(f"Number too large (max supported: 10^18)")

    # Decompose the number into syllables
    # We process from largest to smallest power of 10
    syllables = []
    remaining = number

    # Powers of 10 in descending order
    vowel_powers = sorted(VOWELS.keys(), reverse=True)

    #Reversed list of consonants
    avarga_values = sorted(AVARGA_CONSONANTS.keys(), reverse=True)
    varga_values = sorted(VARGA_CONSONANTS.keys(), reverse=True)

    for vowel_power in vowel_powers:
        if remaining == 0:
            break

        # Find how many times this power fits
        coefficient = remaining // vowel_power

        if coefficient == 0:
            continue

        varga_only = False
        if coefficient < 26:
            varga_only = True

        # Break down the coefficient into consonant values
        # We try to use the largest consonant values first
        coeff_remaining = coefficient
        if not varga_only:
            if coeff_remaining < 30: # Exception for numbers 26-29
                consonant = VARGA_CONSONANTS[20]
                add_syllable(consonant, vowel_power, syllables)

                coeff_remaining -= 20
            else:
                for avarga_val in avarga_values:
                    if avarga_val <= coeff_remaining:
                        # Create syllable: consonant + vowel
                        consonant = AVARGA_CONSONANTS[avarga_val]
                        add_syllable(consonant, vowel_power, syllables)

                        coeff_remaining -= avarga_val
                        break


        for varga_val in varga_values:
            if varga_val <= coeff_remaining:
                # Create syllable: consonant + vowel
                consonant = VARGA_CONSONANTS[varga_val]
                add_syllable(consonant, vowel_power, syllables)
                break

        remaining -= coefficient * vowel_power

    # Reverse syllables so smallest values are on the left, largest on the right
    # (Aryabhata numerals are written from smallest to largest left-to-right)
    return ''.join(reversed(syllables))


def main():
    parser = argparse.ArgumentParser(
        prog="AryabhataCipher",
        description="""Converts numbers to Sanskrit syllables using Aryabhata's numeral system.
        The Aryabhata numeral system is an ancient Indian alphasyllabic numeral system created by
        mathematician Aryabhata (476-550 CE). It uses Sanskrit consonants combined with vowel marks
        to represent numbers from 1 to 10^18. Numerals are written smallest to largest from left to right."""
    )

    parser.add_argument('number',
                        type=int,
                        help="Number to convert to Aryabhata numerals (0 to 10^18)")

    args = parser.parse_args()

    try:
        aryabhata = number_to_aryabhata(args.number)
        #aryabhata = normalize("NFC", aryabhata )
        print(f"Number: {args.number}")
        print(f"Aryabhata: {aryabhata}")
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
