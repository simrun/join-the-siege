import mimetypes

import easyocr
import pdfplumber
from werkzeug.datastructures import FileStorage


# Load EasyOCR model once at startup to avoid reloading per request
reader = easyocr.Reader(['en'], model_storage_directory='models')

class UnsupportedFiletypeError(ValueError):
    pass

def img_to_text(img_file: FileStorage) -> str:
    """
    Extract text from an image file.

    Parameters:
        img_file: The image file to process

    Returns:
        str: Concatenated text
    """
    return "\n".join(reader.readtext(img_file.read(), detail=0))

def pdf_to_text(pdf_file: FileStorage) -> str:
    """
    Extract text from a PDF.

    Parameters:
        pdf_file: The PDF file to process

    Returns:
        str: Concatenated text
    """
    with pdfplumber.open(pdf_file) as pdf:
        return "\n".join(filter(None, (page.extract_text() for page in pdf.pages)))

def file_to_text(file: FileStorage) -> str:
    """
    Extract text from a file.

    Parameters:
        file (FileStorage): The uploaded file

    Returns:
        str: Extracted text content

    Raises:
        UnsupportedFiletypeError: If the filetype is not supported
    """
    match mimetypes.guess_type(file.filename):
        case ('image/jpeg' | 'image/png', None):
            return img_to_text(file)
        case ('application/pdf', None):
            return pdf_to_text(file)
        case s:
            raise UnsupportedFiletypeError(s)
