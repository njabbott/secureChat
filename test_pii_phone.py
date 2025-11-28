"""Test script to verify PII redaction for phone numbers"""

import sys
sys.path.insert(0, '/Users/angelaabbott/PycharmProjects/PythonProject/backend')

from app.services.pii_service import PIIService

# Initialize PII service
pii = PIIService()

# Test cases with different phone number formats
test_cases = [
    "0423 123 456",
    "Call me at 0423 123 456 for more info",
    "Phone: 0423 123 456",
    "0423123456",
    "04 2312 3456",
    "+61 423 123 456",
    "The contact number is 0423 123 456.",
]

print("="*80)
print("Testing PII Redaction for Phone Numbers")
print("="*80)

for i, test_text in enumerate(test_cases, 1):
    print(f"\nTest {i}: '{test_text}'")
    print("-"*80)

    # Test with default placeholders
    anonymized, pii_info = pii.detect_and_anonymize(test_text)
    print(f"Default placeholder:")
    print(f"  Result: '{anonymized}'")
    print(f"  PII detected: {pii_info.total_count} items - {pii_info.entities}")

    # Test with custom replacement (as used in indexing)
    anonymized_custom, pii_info_custom = pii.detect_and_anonymize(
        test_text,
        replacement_text="[PII redacted]"
    )
    print(f"\nCustom '[PII redacted]' placeholder:")
    print(f"  Result: '{anonymized_custom}'")
    print(f"  PII detected: {pii_info_custom.total_count} items - {pii_info_custom.entities}")

    # Check if partial redaction occurred
    if "[PII redacted]" in anonymized_custom or "[PHONE]" in anonymized:
        # Check if any digits remain in the anonymized text
        remaining_digits = ''.join(c for c in anonymized_custom if c.isdigit())
        if remaining_digits:
            print(f"\n  ⚠️  WARNING: Partial redaction detected! Remaining digits: {remaining_digits}")

    print()
