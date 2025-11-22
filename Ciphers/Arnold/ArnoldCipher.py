#!/usr/bin/env python3
"""
Arnold Cipher Encoder
Encodes English words into Arnold Cipher references (Page.Line.Word) by finding them in PDF files.
Supports both "Commentaries on the Laws of England" and "Nathan Bailey's Dictionary".
"""

import sys, re, argparse

# Try to import PDF libraries (prefer pdfplumber for better text extraction)
PDF_LIBRARY = None
try:
    import pdfplumber
    PDF_LIBRARY = 'pdfplumber'
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = 'PyPDF2'
    except ImportError:
        print("Error: A PDF library is required.")
        print("Install one of the following:")
        print("  pip install pdfplumber  (recommended)")
        print("  pip install PyPDF2")
        sys.exit(1)


def extract_text_from_pdf(pdf_path, page_num):
    """
    Extract text from a specific page of a PDF.

    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (1-indexed)

    Returns:
        Text content of the page as a string
    """
    try:
        if PDF_LIBRARY == 'pdfplumber':
            with pdfplumber.open(pdf_path) as pdf:
                if page_num < 1 or page_num > len(pdf.pages):
                    raise ValueError(f"Page {page_num} out of range (1-{len(pdf.pages)})")

                # pdfplumber uses 0-indexed pages
                page = pdf.pages[page_num - 1]
                text = page.extract_text()
                return text if text else ""

        elif PDF_LIBRARY == 'PyPDF2':
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)

                if page_num < 1 or page_num > len(pdf_reader.pages):
                    raise ValueError(f"Page {page_num} out of range (1-{len(pdf_reader.pages)})")

                # PyPDF2 uses 0-indexed pages
                page = pdf_reader.pages[page_num - 1]
                text = page.extract_text()
                return text if text else ""

    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Error reading PDF: {e}")


def get_page_count(pdf_path):
    """
    Get the total number of pages in a PDF.

    Args:
        pdf_path: Path to the PDF file

    Returns:
        Number of pages in the PDF
    """
    try:
        if PDF_LIBRARY == 'pdfplumber':
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        elif PDF_LIBRARY == 'PyPDF2':
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
    except Exception as e:
        raise Exception(f"Error getting page count: {e}")


def find_word_in_pdf(pdf_path, target_word, case_sensitive=False):
    """
    Find the first occurrence of a word in a PDF and return its Page.Line.Word reference.

    Args:
        pdf_path: Path to the PDF file
        target_word: Word to find
        case_sensitive: Whether to match case-sensitively (default: False)

    Returns:
        Tuple of (page_num, line_num, word_num) or None if not found
    """
    # Clean the target word (remove punctuation for matching)
    clean_target = re.sub(r'[^\w\'-]', '', target_word)

    if not case_sensitive:
        clean_target = clean_target.lower()

    # Get total pages
    total_pages = get_page_count(pdf_path)

    # Search through each page
    for page_num in range(1, total_pages + 1):
        # Extract text from page
        page_text = extract_text_from_pdf(pdf_path, page_num)

        # Split into lines
        lines = page_text.split('\n')

        # Filter out empty lines for consistent line counting
        lines = [line for line in lines if line.strip()]

        # Search through each line
        for line_num, line in enumerate(lines, start=1):
            # Split line into words
            words = line.split()

            # Search through each word
            for word_num, word in enumerate(words, start=1):
                # Clean the word (remove punctuation)
                clean_word = re.sub(r'[^\w\'-]', '', word)

                # Compare words
                compare_word = clean_word if case_sensitive else clean_word.lower()

                if compare_word == clean_target:
                    return (page_num, line_num, word_num)

    # Word not found
    return None


def encode_arnold_cipher(pdf_path, words, case_sensitive=False):
    """
    Encode a list of words into Arnold Cipher references.

    Args:
        pdf_path: Path to the PDF file
        words: List of words to encode
        case_sensitive: Whether to match case-sensitively (default: False)

    Returns:
        List of cipher references in format "Page.Line.Word"
    """
    cipher_refs = []
    not_found_words = []

    for word in words:
        word = word.strip()
        if not word:
            continue

        result = find_word_in_pdf(pdf_path, word, case_sensitive)

        if result:
            page_num, line_num, word_num = result
            cipher_ref = f"{page_num}.{line_num}.{word_num}"
            cipher_refs.append(cipher_ref)
        else:
            not_found_words.append(word)
            cipher_refs.append(f"[NOT_FOUND:{word}]")

    # If any words weren't found, raise an error
    if not_found_words:
        error_msg = f"The following word(s) could not be found in the PDF: {', '.join(not_found_words)}"
        raise ValueError(error_msg)

    return cipher_refs


def main():
    parser = argparse.ArgumentParser(
        prog='ArnoldEncipher',
        description="""Encodes words into Arnold Cipher references. Takes English words and finds them in a reference PDF,
                       returning their location as ###.##.## for Page.Line.Word respectively. This is also known as a book cipher.

                       Meant to work with shared reference material like a book. The first occurrence of each word
                       in the PDF will be used.

                       Historically reference books used for this cipher were "Commentaries on the Laws of England" by William
                       Blackstone and "Nathan Bailey's Dictionary". Used by General Benedict Arnold in an attempt to surrender
                       West Point to the British during the Revolutionary war. He did not succeed."""
    )
    parser.add_argument('reference_material',
                        type=str,
                        help="PDF file to use as reference when encoding")
    parser.add_argument('words',
                        type=str,
                        help="Space-separated words to encode (e.g., 'hello world secret message')")
    parser.add_argument('-c', '--case-sensitive',
                        action='store_true',
                        help="Match words case-sensitively (default: case-insensitive)")
    args = parser.parse_args()

    pdf_path = args.reference_material
    words = args.words.split()

    try:
        # Encode all words
        cipher_refs = encode_arnold_cipher(pdf_path, words, args.case_sensitive)

        # Display results
        if len(words) == 1:
            print(cipher_refs[0])
        else:
            print("\nEncoded message:")
            for word, ref in zip(words, cipher_refs):
                print(f"  {word:20} -> {ref}")
            print("\nCipher text:", ' '.join(cipher_refs))

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
