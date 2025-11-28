"""PII detection and anonymization service using Microsoft Presidio"""

import logging
import re
from typing import Dict, Tuple
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from ..models.chat import PIIInfo

logger = logging.getLogger(__name__)


class PIIService:
    """Service for detecting and anonymizing PII using Microsoft Presidio"""

    def __init__(self):
        """Initialize Presidio analyzer and anonymizer"""
        try:
            self.analyzer = AnalyzerEngine()
            self.anonymizer = AnonymizerEngine()

            # Add custom recognizer for Australian phone numbers
            self._add_australian_phone_recognizer()

            logger.info("Initialized PII service with Presidio and custom Australian phone recognizer")

        except Exception as e:
            logger.error(f"Error initializing PII service: {e}")
            logger.warning("PII detection may not work properly. Install spaCy model: python -m spacy download en_core_web_lg")
            # Create dummy engines that will fail gracefully
            self.analyzer = None
            self.anonymizer = None

    def _add_australian_phone_recognizer(self):
        """Add custom recognizer for Australian phone number formats"""
        # Australian phone number patterns
        au_phone_patterns = [
            # Mobile: 04XX XXX XXX with various separators
            Pattern(
                name="au_mobile_spaced",
                regex=r"\b0[45]\d{2}\s?\d{3}\s?\d{3}\b",
                score=0.7,
            ),
            # Landline: (0X) XXXX XXXX or 0X XXXX XXXX
            Pattern(
                name="au_landline",
                regex=r"\b\(?0[2378]\)?\s?\d{4}\s?\d{4}\b",
                score=0.7,
            ),
            # International format: +61 XXX XXX XXX
            Pattern(
                name="au_international",
                regex=r"\+61\s?[45]\d{2}\s?\d{3}\s?\d{3}\b",
                score=0.8,
            ),
            # Partial phone numbers (6+ consecutive digits starting with 0)
            Pattern(
                name="au_partial_phone",
                regex=r"\b0\d{5,}\b",
                score=0.6,
            ),
        ]

        au_phone_recognizer = PatternRecognizer(
            supported_entity="AU_PHONE_NUMBER",
            patterns=au_phone_patterns,
            context=["phone", "mobile", "call", "contact", "tel", "telephone", "fax"],
        )

        # Add the recognizer to the analyzer
        self.analyzer.registry.add_recognizer(au_phone_recognizer)

    def detect_and_anonymize(self, text: str, replacement_text: str = None) -> Tuple[str, PIIInfo]:
        """
        Detect and anonymize PII in text

        Args:
            text: Input text to scan for PII
            replacement_text: Custom replacement text (default: use specific placeholders)

        Returns:
            Tuple of (anonymized_text, pii_info)
        """
        if not self.analyzer or not self.anonymizer:
            logger.warning("PII service not properly initialized, returning original text")
            return text, PIIInfo(total_count=0, entities={})

        try:
            # Analyze text for PII
            results = self.analyzer.analyze(
                text=text,
                language="en",
                entities=[
                    "PERSON",
                    "EMAIL_ADDRESS",
                    "PHONE_NUMBER",
                    "AU_PHONE_NUMBER",  # Custom Australian phone recognizer
                    "CREDIT_CARD",
                    "US_SSN",
                    "US_PASSPORT",
                    "LOCATION",
                    "DATE_TIME",
                    "IP_ADDRESS",
                    "URL",
                    "US_DRIVER_LICENSE",
                    "IBAN_CODE",
                    "NRP",  # National Registry of Persons
                    "MEDICAL_LICENSE",
                    "US_BANK_NUMBER",
                ],
            )

            # If no PII detected, return original text
            if not results:
                return text, PIIInfo(total_count=0, entities={})

            # Count entities by type
            entity_counts: Dict[str, int] = {}
            for result in results:
                entity_type = result.entity_type
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

            # Anonymize the text
            if replacement_text:
                # Use custom replacement text for all PII types
                anonymized_result = self.anonymizer.anonymize(
                    text=text,
                    analyzer_results=results,
                    operators={
                        "DEFAULT": OperatorConfig("replace", {"new_value": replacement_text}),
                    },
                )
            else:
                # Use specific placeholders for each PII type
                anonymized_result = self.anonymizer.anonymize(
                    text=text,
                    analyzer_results=results,
                    operators={
                        "DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"}),
                        "PERSON": OperatorConfig("replace", {"new_value": "[PERSON_NAME]"}),
                        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "[EMAIL]"}),
                        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
                        "AU_PHONE_NUMBER": OperatorConfig("replace", {"new_value": "[PHONE]"}),
                        "CREDIT_CARD": OperatorConfig("replace", {"new_value": "[CREDIT_CARD]"}),
                        "US_SSN": OperatorConfig("replace", {"new_value": "[SSN]"}),
                        "LOCATION": OperatorConfig("replace", {"new_value": "[LOCATION]"}),
                        "DATE_TIME": OperatorConfig("replace", {"new_value": "[DATE]"}),
                        "IP_ADDRESS": OperatorConfig("replace", {"new_value": "[IP_ADDRESS]"}),
                        "US_PASSPORT": OperatorConfig("replace", {"new_value": "[PASSPORT]"}),
                    },
                )

            anonymized_text = anonymized_result.text
            total_count = len(results)

            # Create PII info
            pii_info = PIIInfo(total_count=total_count, entities=entity_counts)

            logger.info(f"Detected and anonymized {total_count} PII entities: {entity_counts}")

            return anonymized_text, pii_info

        except Exception as e:
            logger.error(f"Error during PII detection/anonymization: {e}")
            # On error, return original text but log the issue
            return text, PIIInfo(total_count=0, entities={})

    def detect_only(self, text: str) -> PIIInfo:
        """
        Detect PII without anonymizing

        Args:
            text: Input text to scan for PII

        Returns:
            PIIInfo object with detection results
        """
        if not self.analyzer:
            return PIIInfo(total_count=0, entities={})

        try:
            results = self.analyzer.analyze(text=text, language="en")

            entity_counts: Dict[str, int] = {}
            for result in results:
                entity_type = result.entity_type
                entity_counts[entity_type] = entity_counts.get(entity_type, 0) + 1

            total_count = len(results)
            return PIIInfo(total_count=total_count, entities=entity_counts)

        except Exception as e:
            logger.error(f"Error during PII detection: {e}")
            return PIIInfo(total_count=0, entities={})
