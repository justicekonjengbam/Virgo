import re
from pathlib import Path


class DocumentValidationError(Exception):
    """Raised when an uploaded document fails security, format, or malware validation."""
    pass


ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.webp'}

# Magic byte signatures for authorized document formats
MAGIC_SIGNATURES = [
    ('application/pdf', b'%PDF-'),
    ('image/jpeg', b'\xff\xd8\xff'),
    ('image/png', b'\x89PNG\r\n\x1a\n'),
]

# Disallowed binary executable headers that must never be present
DANGEROUS_BINARY_HEADERS = [
    (b'MZ', 'Windows Portable Executable (PE/EXE/DLL)'),
    (b'\x7fELF', 'Linux Executable and Linkable Format (ELF)'),
    (b'PK\x03\x04', 'ZIP / Archive container'),
    (b'Rar!\x1a\x07', 'RAR archive container'),
    (b'7z\xbc\xaf\x27\x1c', '7-Zip archive container'),
]

# Active PDF exploit and execution triggers
PDF_DANGEROUS_ACTIONS = [
    (b'/JavaScript', 'Embedded PDF JavaScript execution'),
    (b'/JS', 'Embedded PDF JavaScript trigger'),
    (b'/Launch', 'External application execution launch action'),
    (b'/EmbeddedFiles', 'Embedded executable attachments'),
    (b'/RichMedia', 'Embedded Flash or active rich media'),
]

# Web script / payload markers (scanned across the entire file)
SCRIPT_PATTERNS = [
    re.compile(rb'<\s*script', re.IGNORECASE),
    re.compile(rb'<\s*iframe', re.IGNORECASE),
    re.compile(rb'<\s*object', re.IGNORECASE),
    re.compile(rb'<\s*embed', re.IGNORECASE),
    re.compile(rb'<\s*html', re.IGNORECASE),
    re.compile(rb'<\s*\?php', re.IGNORECASE),
    re.compile(rb'<\s*%=', re.IGNORECASE),
    re.compile(rb'javascript\s*:', re.IGNORECASE),
    re.compile(rb'vbscript\s*:', re.IGNORECASE),
    re.compile(rb'data\s*:\s*text\/html', re.IGNORECASE),
]


def detect_mime_type(data: bytes) -> str | None:
    """Inspects raw file header bytes to reliably determine actual content type."""
    if len(data) < 4:
        return None

    # Check known fixed signatures
    for mime, prefix in MAGIC_SIGNATURES:
        if data.startswith(prefix):
            return mime

    # WebP check: RIFF header with WEBP marker at offset 8
    if len(data) >= 12 and data[:4] == b'RIFF' and data[8:12] == b'WEBP':
        return 'image/webp'

    return None


def scan_file_for_malware(filename: str, file_bytes: bytes, detected_mime: str) -> None:
    """
    Scans document content for active executable code, script payloads,
    malicious PDF features, and binary execution constructs.
    """
    # 1. Reject disguised executable headers
    for magic, label in DANGEROUS_BINARY_HEADERS:
        if file_bytes.startswith(magic):
            raise DocumentValidationError(f"File rejected: Detected {label} signature.")

    # 2. Check for script and markup injections across the entire file
    # For images (JPEG, PNG, WebP), no script/HTML/PHP patterns are permitted anywhere
    if detected_mime.startswith('image/'):
        for pattern in SCRIPT_PATTERNS:
            if pattern.search(file_bytes):
                raise DocumentValidationError("File rejected: Image contains embedded script or markup content.")

    # 3. PDF Active Code Scanning
    if detected_mime == 'application/pdf':
        # Check for dangerous PDF actions
        for action, desc in PDF_DANGEROUS_ACTIONS:
            if action in file_bytes:
                raise DocumentValidationError(f"File rejected: PDF contains disallowed active content ({desc}).")

        # Check for embedded script / web tags in PDF body outside streams
        for pattern in SCRIPT_PATTERNS:
            if pattern.search(file_bytes):
                raise DocumentValidationError("File rejected: PDF contains disallowed executable script or markup.")


def validate_document_file(
    filename: str,
    file_bytes: bytes,
    declared_content_type: str | None = None,
    max_size_bytes: int = 5 * 1024 * 1024,
) -> tuple[str, str]:
    """
    Validates document security constraints, content type, and scans for malware.
    Returns (actual_mime_type, normalized_extension).
    Raises DocumentValidationError if validation fails.
    """
    if not file_bytes or len(file_bytes) == 0:
        raise DocumentValidationError("The uploaded file is empty.")

    if len(file_bytes) > max_size_bytes:
        max_mb = max_size_bytes // (1024 * 1024)
        raise DocumentValidationError(f"File size exceeds the {max_mb} MB limit.")

    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise DocumentValidationError(f"Invalid file extension '{ext}'. Allowed extensions: {allowed}")

    # 1. Immediate scan for disguised binary executable / archive headers
    for magic, label in DANGEROUS_BINARY_HEADERS:
        if file_bytes.startswith(magic):
            raise DocumentValidationError(f"File rejected: Detected {label} signature.")

    # Detect actual content type from magic bytes
    actual_mime = detect_mime_type(file_bytes)
    if not actual_mime:
        raise DocumentValidationError(
            "File content signature does not match any accepted document format (PDF, JPEG, PNG, WebP)."
        )

    # Validate that extension matches actual magic-byte content
    ext_mime_map = {
        '.pdf': 'application/pdf',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.webp': 'image/webp',
    }
    expected_mime = ext_mime_map.get(ext)
    if expected_mime != actual_mime:
        raise DocumentValidationError(
            f"File extension '{ext}' does not match actual detected file content ({actual_mime})."
        )

    # Comprehensive malware and active content scan
    scan_file_for_malware(filename, file_bytes, actual_mime)

    return actual_mime, ext
