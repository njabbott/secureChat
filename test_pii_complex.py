"""Test script for complex PII scenarios that might cause partial redaction"""

import sys
sys.path.insert(0, '/Users/angelaabbott/PycharmProjects/PythonProject/backend')

from app.services.pii_service import PIIService
from presidio_analyzer import AnalyzerEngine

# Initialize services
pii = PIIService()
analyzer = AnalyzerEngine()

# Test cases that might cause partial redaction
test_cases = [
    # Multiple phone numbers in sequence
    "0423 123 456 or 0423 123 789",

    # Phone number with additional context
    "The emergency contact is John Smith at 0423 123 456",

    # Partial phone number formatting issues
    "Call 0423 123 [PII redacted]",  # Simulating what user reported

    # Mixed with other numbers
    "Order #12345 from 0423 123 456",

    # Phone number after being indexed (already redacted)
    "Contact: [PII redacted]",

    # Phone number that might be split across text
    "Contact 0423\n123\n456",
]

print("="*80)
print("Complex PII Redaction Tests")
print("="*80)

for i, test_text in enumerate(test_cases, 1):
    print(f"\nTest {i}: '{test_text}'")
    print("-"*80)

    # First, show what the analyzer detects
    results = analyzer.analyze(
        text=test_text,
        language="en",
        entities=["PHONE_NUMBER", "PERSON", "DATE_TIME"]
    )

    print("Analyzer Detection:")
    for result in results:
        detected_text = test_text[result.start:result.end]
        print(f"  - Type: {result.entity_type}, Text: '{detected_text}', "
              f"Position: {result.start}-{result.end}, Score: {result.score:.2f}")

    # Then anonymize with custom replacement
    anonymized, pii_info = pii.detect_and_anonymize(
        test_text,
        replacement_text="[PII redacted]"
    )

    print(f"\nAnonymized Result:")
    print(f"  '{anonymized}'")
    print(f"  PII Count: {pii_info.total_count}, Entities: {pii_info.entities}")

    # Check for any remaining digits
    remaining_digits = ''.join(c for c in anonymized if c.isdigit())
    if remaining_digits and "[PII redacted]" in anonymized:
        print(f"  ⚠️  WARNING: Digits remain after redaction: '{remaining_digits}'")

    print()

# Special test: What if OpenAI returns a document that was already partially redacted?
print("\n" + "="*80)
print("HYPOTHESIS TEST: What if the issue is in the vector DB?")
print("="*80)

# Simulate a scenario where a document might have been incompletely redacted
possibly_bad_docs = [
    "The support hotline is 0423 123 [PII redacted]",  # What user reported
    "Call us: 0423 [PII redacted] 456",
]

for doc in possibly_bad_docs:
    print(f"\nDocument in DB: '{doc}'")

    # Try to redact it again
    re_anonymized, pii_info = pii.detect_and_anonymize(
        doc,
        replacement_text="[PII redacted]"
    )

    print(f"Re-anonymized: '{re_anonymized}'")
    print(f"PII detected: {pii_info.total_count} items - {pii_info.entities}")