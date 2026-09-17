# =====================================================
# CAMPUSMIND AI
# FILE PROCESSING SERVICE (PDF & Images)
# =====================================================

import io
import base64
from pypdf import PdfReader


class FileProcessingError(Exception):
    """Custom exception for file processing failures."""
    pass


def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 25, max_chars: int = 50000) -> dict:
    """
    Extracts readable text from PDF bytes.
    
    Args:
        pdf_bytes: Raw bytes of the uploaded PDF file.
        max_pages: Maximum number of pages to process.
        max_chars: Maximum characters to extract to prevent token overflow.
        
    Returns:
        dict: {
            "page_count": int,
            "extracted_text": str,
            "is_truncated": bool
        }
    """
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        pages_to_read = min(total_pages, max_pages)

        extracted_parts = []
        char_count = 0
        is_truncated = total_pages > max_pages

        for idx in range(pages_to_read):
            page = reader.pages[idx]
            page_text = page.extract_text() or ""
            page_text = page_text.strip()

            if page_text:
                header = f"--- Page {idx + 1} ---"
                chunk = f"{header}\n{page_text}\n"

                if char_count + len(chunk) > max_chars:
                    remaining = max_chars - char_count
                    if remaining > 50:
                        extracted_parts.append(chunk[:remaining] + "\n...[Content truncated for length]...")
                    is_truncated = True
                    break

                extracted_parts.append(chunk)
                char_count += len(chunk)

        full_text = "\n".join(extracted_parts).strip()

        if not full_text:
            full_text = "[Notice: This PDF contains scanned images or non-selectable text.]"

        return {
            "total_pages": total_pages,
            "processed_pages": pages_to_read,
            "extracted_text": full_text,
            "is_truncated": is_truncated
        }

    except Exception as exc:
        raise FileProcessingError(f"Failed to read PDF document: {str(exc)}") from exc


def process_image_to_data_url(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """
    Converts raw image bytes into a base64 Data URL for multimodal LLM vision.
    
    Args:
        image_bytes: Raw bytes of the uploaded image.
        mime_type: MIME type string (e.g. 'image/png', 'image/jpeg', 'image/webp').
        
    Returns:
        str: 'data:image/jpeg;base64,...'
    """
    if not mime_type or not mime_type.startswith("image/"):
        mime_type = "image/jpeg"

    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
