from src.core.logger import StructuredLogger

class TLDRValidationError(Exception):
    """Raised when TLDR validation fails"""
    pass

def parse_tldr(response: str, logger: StructuredLogger) -> str:
    """
    Parse the TLDR from LLM Response

    Args:
        response: Raw LLM response text
        logger: Structured Logger instance

    Returns:
        Cleaned TLDR string

    Raises:
        TLDRValidationError: If response is empty
    """
    if not response or not response.strip():
        raise TLDRValidationError("Empty response from LLM")

    tldr = response.strip().replace("**", "").replace("*", "")

    prefixes_to_remove = [
        "TLDR:",
        "TL;DR",
        "Summary:",
        "Here's The TLDR:",
        "TLDR -"
    ]

    for prefix in prefixes_to_remove:
        if tldr.upper().startswith(prefix.upper()):
            tldr = tldr[len(prefix):].strip()

    if (tldr.startswith('"') and tldr.endswith('"')) or \
       (tldr.startswith("'") and tldr.endswith("'")):
        tldr = tldr[1:-1].strip()

    # Log word count for monitoring, but don't fail
    word_count = len(tldr.split())
    if word_count < 8 or word_count > 16:
        logger.info(event_type="llm_summary run", message=f"TLDR word count outside 8-16 range ({word_count} words): {tldr}")

    return tldr
