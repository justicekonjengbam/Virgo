"""
Phone number normalization and multi-format variant resolution.
Ensures E.164, local 10-digit, and un-prefixed formats resolve consistently.
"""

def normalize_phone_e164(phone: str) -> str:
    """Normalize any Indian mobile input to canonical +91XXXXXXXXXX format."""
    digits = "".join(c for c in phone if c.isdigit())
    if len(digits) == 10 and digits[0] in "6789":
        return f"+91{digits}"
    if len(digits) == 12 and digits.startswith("91") and digits[2] in "6789":
        return f"+{digits}"
    raise ValueError("Enter a valid 10-digit Indian mobile number.")


def phone_variants(phone: str) -> list[str]:
    """
    Return all valid representation variants of a phone number.
    e.g. For +919876543210 -> ['+919876543210', '919876543210', '9876543210', '+9876543210']
    """
    raw = phone.strip()
    digits = "".join(c for c in raw if c.isdigit())
    variants = {raw}
    if digits:
        variants.add(digits)
        variants.add(f"+{digits}")
        if len(digits) == 10:
            variants.add(f"91{digits}")
            variants.add(f"+91{digits}")
        elif len(digits) == 12 and digits.startswith("91"):
            local_10 = digits[2:]
            variants.add(local_10)
            variants.add(f"+91{local_10}")
            variants.add(f"91{local_10}")
            variants.add(f"+{local_10}")
    return list(variants)

