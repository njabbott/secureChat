# PII Redaction Requirements

## Overview
All Personally Identifiable Information (PII) must be detected and redacted from responses before being shown to users. This is a **critical security requirement**.

## Required PII Types to Redact

### 1. Phone Numbers
**MUST redact ALL phone number formats:**

#### Australian Phone Numbers (HIGH PRIORITY)
- **Mobile numbers:** `04XX XXX XXX` (e.g., `0413 234 123`, `0423456789`)
- **Landline numbers:** `(0X) XXXX XXXX` or `0X XXXX XXXX` (e.g., `(02) 1234 5678`, `03 9876 5432`)
- **International format:** `+61 X XXXX XXXX` (e.g., `+61 4 1234 5678`)
- **Partial numbers:** Any sequence starting with `0` followed by 6+ digits

#### International Phone Numbers
- **US numbers:** `(XXX) XXX-XXXX`, `XXX-XXX-XXXX`
- **UK numbers:** `+44 XXXX XXXXXX`
- **Generic:** `+XX X XXXX XXXX`

### 2. Personal Information
- **Person names:** Full names, first names with last initials
- **Email addresses:** All email formats
- **Physical addresses:** Street addresses, PO boxes
- **Credit card numbers:** All formats
- **Government IDs:** SSN, passport numbers, driver's licenses, Medicare numbers

### 3. Other Sensitive Data
- **IP addresses:** IPv4 and IPv6
- **Dates of birth:** All date formats
- **Medical information:** Medical license numbers, patient IDs
- **Financial information:** Bank account numbers, IBAN codes

## Redaction Format
- Replace ALL detected PII with: `[PII redacted]`
- This format is consistent and user-friendly

## Testing Requirements

### Critical Test Cases (MUST PASS)

#### Test Case 1: Australian Mobile Numbers with Spaces
```
Input:  "Contact Nick on 0413 234 123"
Output: "Contact Nick on [PII redacted]"
Status: REQUIRED ✅
```

#### Test Case 2: Australian Mobile Numbers without Spaces
```
Input:  "Call 0423456789"
Output: "Call [PII redacted]"
Status: REQUIRED ✅
```

#### Test Case 3: Multiple Phone Numbers
```
Input:  "Nick: 0413 234 123, Jo: 0423 456 789"
Output: "Nick: [PII redacted], Jo: [PII redacted]"
Status: REQUIRED ✅
```

#### Test Case 4: Phone Numbers in Context
```
Input:  "For support, call our helpline on 1300 123 456 or mobile 0412 345 678"
Output: "For support, call our helpline on [PII redacted] or mobile [PII redacted]"
Status: REQUIRED ✅
```

#### Test Case 5: Names and Emails
```
Input:  "Contact john.smith@example.com for details"
Output: "Contact [PII redacted] for details"
Status: REQUIRED ✅
```

### Regression Testing
**Before ANY deployment:**
1. Run all PII test cases
2. Verify initialization logs show NO errors
3. Check that PII service is "properly initialized"
4. Test with real-world examples from production data

## Implementation Requirements

### 1. Service Initialization
- PII service MUST initialize successfully on startup
- MUST log clear error messages if initialization fails
- MUST NOT silently fail and return unredacted text
- Configuration MUST include proper `lang_code` for spaCy models

### 2. Error Handling
- If PII service fails to initialize: **BLOCK application startup**
- Do NOT start the application if PII redaction is not working
- This is a security requirement - failing open is NOT acceptable

### 3. Logging
- MUST log when PII is detected: count and types
- MUST log initialization status clearly
- MUST log errors with full context for debugging

### 4. Monitoring
- Track PII detection rate in metrics
- Alert if PII detection drops significantly (indicates service failure)
- Monitor initialization errors in production

## Verification Checklist

Before marking PII work as "done":
- [ ] All test cases pass (see Critical Test Cases above)
- [ ] No initialization errors in logs
- [ ] Service logs confirm "Initialized PII service with Presidio and custom Australian phone recognizer"
- [ ] Tested with real examples from production/Confluence
- [ ] Verified phone numbers in multiple formats are redacted
- [ ] Checked that names and emails are redacted
- [ ] Confirmed replacement text is `[PII redacted]`

## Configuration Files

### Required spaCy Model
- Model: `en_core_web_sm`
- Must be installed in Docker container
- Must include proper `lang_code` configuration

### Presidio Configuration
```python
# NLP engine MUST be configured with lang_code
nlp_config = NlpEngineConfig(
    models=[{"lang_code": "en", "model_name": "en_core_web_sm"}]
)
```

## Failure Scenarios to Prevent

### ❌ NEVER Allow These
1. **Silent Failure:** PII service fails but returns unredacted text
2. **Partial Redaction:** Some PII types work, others don't
3. **Inconsistent Format:** Using different replacement strings
4. **Missing Initialization:** Service not properly configured at startup
5. **No Testing:** Deploying without running test cases

## How to Prevent Bugs

### 1. Automated Testing (REQUIRED)
Create `backend/tests/test_pii_service.py` with all critical test cases.
Run tests before every deployment.

### 2. Integration Testing
Test end-to-end flow: User query → PII detection → OpenAI response → PII redaction

### 3. Code Review Checklist
- [ ] PII service initialization includes `lang_code`
- [ ] Error handling doesn't silently fail
- [ ] All new PII types are added to test cases
- [ ] Logs clearly indicate PII detection status

### 4. Deployment Checklist
- [ ] Run PII tests
- [ ] Check Docker logs for initialization errors
- [ ] Test with real phone numbers
- [ ] Verify `[PII redacted]` appears in responses

## Document History
- 2026-01-04: Created after production bug where phone numbers were not redacted due to missing `lang_code` in spaCy configuration
