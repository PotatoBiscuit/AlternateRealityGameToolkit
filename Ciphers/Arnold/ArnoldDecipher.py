#!/usr/bin/env python3
"""
Arnold Cipher Decoder
Decodes Arnold Cipher references (Page.Line.Word) from PDF files.
Supports both "Commentaries on the Laws of England" and "Nathan Bailey's Dictionary"
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


def decode_arnold_cipher(pdf_path, cipher_ref):
    """
    Decode an Arnold Cipher reference.

    Args:
        pdf_path: Path to the PDF file
        cipher_ref: Cipher reference in format "Page.Line.Word"

    Returns:
        The decoded word
    """
    # Parse the cipher reference
    match = re.match(r'^(\d+)\.(\d+)\.(\d+)$', cipher_ref)
    if not match:
        raise ValueError(f"Invalid cipher format: '{cipher_ref}'. Expected format: Page.Line.Word (e.g., 120.9.7)")

    page_num = int(match.group(1))
    line_num = int(match.group(2))
    word_num = int(match.group(3))

    # Extract text from the specified page
    page_text = extract_text_from_pdf(pdf_path, page_num)

    # Split into lines
    lines = page_text.split('\n')

    # Filter out empty lines for more consistent line counting
    lines = [line for line in lines if line.strip()]

    # Check line number
    if line_num < 1 or line_num > len(lines):
        raise ValueError(f"Line {line_num} out of range on page {page_num} (1-{len(lines)} non-empty lines)")

    # Get the specified line (1-indexed)
    target_line = lines[line_num - 1]

    # Split line into words
    words = target_line.split()

    # Check word number
    if word_num < 1 or word_num > len(words):
        raise ValueError(f"Word {word_num} out of range on page {page_num}, line {line_num} (1-{len(words)} words)")

    # Get the specified word (1-indexed)
    target_word = words[word_num - 1]

    # Clean the word (remove common punctuation)
    target_word = re.sub(r'[^\w\'-]', '', target_word)

    return target_word


def decode_multiple_references(pdf_path, cipher_refs):
    """
    Decode multiple Arnold Cipher references.

    Args:
        pdf_path: Path to the PDF file
        cipher_refs: List of cipher references

    Returns:
        List of decoded words
    """
    words = []
    for ref in cipher_refs:
        try:
            word = decode_arnold_cipher(pdf_path, ref.strip())
            words.append(word)
        except Exception as e:
            print(f"Error decoding '{ref}': {e}", file=sys.stderr)
            words.append(f"[ERROR:{ref}]")

    return words


def main():
    parser = argparse.ArgumentParser(
        prog='ArnoldDecipher',
        description="""Decodes the Arnold Cipher. Encoded words take the form of ###.##.## for Page.Line.Word respectively.
                       Meant to work with shared reference material like a book, where you can flip to page ###, go to line ##,
                       and pick out word ## to form part of the deciphered message. This is also considered a book cipher.

                       Historically reference books used for this cipher were "Commentaries on the Laws of England" by William
                       Blackstone and "Nathan Bailey's Dictionary". Used by General Benedict Arnold in an attempt to surrender
                       West Point to the British during the Revolutionary war. He did not succeed."""
    )
    parser.add_argument('reference_material',
                            type=str,
                            help="Pdf file to reference when decoding")
    parser.add_argument('secret_message',
                            type=str,
                            help="Space separated encoded message like '125.34.3 50.2.3 323.1.4'")
    args = parser.parse_args()

    pdf_path = args.reference_material
    cipher_refs = args.secret_message.split()

    try:
        # Decode all references
        decoded_words = decode_multiple_references(pdf_path, cipher_refs)

        # Display results
        if len(cipher_refs) == 1:
            print(decoded_words[0])
        else:
            print("\nDecoded message:")
            for ref, word in zip(cipher_refs, decoded_words):
                print(f"  {ref:15} -> {word}")
            print("\nFull message:", ' '.join(decoded_words))

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
