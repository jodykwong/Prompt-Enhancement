# Story 5.1: Error Classification and User-Friendly Messages

**Epic**: Epic 5: Robust Error Handling & Graceful Degradation
**Priority**: High
**Acceptance Criteria**: 5
**Status**: Ready for Development

## Overview

The system must classify errors into 5 clear categories and provide specific, user-friendly guidance for each error type. No technical jargon, no internal codes—just clear explanations and resolution steps.

## Acceptance Criteria

### AC1: Error Classification into 5 Categories

**Given** an error occurs during system operation
**When** error is caught
**Then** system classifies into one of 5 categories:

1. **API_KEY_MISSING** - Both OPENAI_API_KEY and DEEPSEEK_API_KEY not found
2. **PROJECT_NOT_DETECTED** - Unable to identify project type
3. **DETECTION_FAILED** - Standards detection confidence <60%
4. **API_TIMEOUT** - LLM API call exceeds 20 seconds
5. **PERMISSION_DENIED** - Cannot access some project files

---

### AC2: API_KEY_MISSING Error Message

**Given** API_KEY_MISSING error occurs
**When** displaying error
**Then** system shows:

```
❌ API Key Not Configured

Please set your OpenAI API key:
1. Run: /pe-setup
2. Or export: export OPENAI_API_KEY=sk-...
3. Or add to ~/.prompt-enhancement/config.yaml
```

**Acceptance Criteria Details:**
- Clear error emoji (❌)
- Specific problem statement
- 3 concrete resolution options
- No technical jargon
- Actionable steps user can take immediately

---

### AC3: PROJECT_NOT_DETECTED Error Message

**Given** PROJECT_NOT_DETECTED error occurs
**When** displaying error
**Then** system shows:

```
⚠️ Project Type Not Detected

System could not identify project language.
Suggestions:
1. Ensure you are in project root directory
2. Project should contain package.json, requirements.txt, etc.
3. System will use generic enhancement
```

**Acceptance Criteria Details:**
- Warning emoji (⚠️) for non-fatal issues
- Clear explanation of what failed
- Troubleshooting suggestions
- Clear indication of fallback behavior

---

### AC4: DETECTION_FAILED Error Message

**Given** DETECTION_FAILED error occurs (standards confidence <60%)
**When** displaying error
**Then** system shows:

```
⚠️ Low Confidence in Standard Detection

System has low confidence in detected standards (Confidence: XX%)
You can:
1. Confirm detected standards
2. Use --override to manually set standards
3. Create .pe.yaml configuration in project
```

**Acceptance Criteria Details:**
- Show actual confidence percentage
- Provide 3 ways to proceed
- Include pointer to template system
- Encourage user action without blocking

---

### AC5: Standard Error Message Format

**Given** error message displayed to user
**When** choosing format and language
**Then** system ensures:
- Clear symptom indicated by emoji (❌ for critical, ⚠️ for warning)
- Simple, plain English (or user's configured language)
- Specific resolution steps (not generic advice)
- No technical jargon, internal codes, or stack traces

**Additional error categories:**
- **API_TIMEOUT**: "LLM API is taking too long. Please retry or check your connection."
- **PERMISSION_DENIED**: "Cannot access some project files. Using available files for analysis."

---

## Technical Requirements

### Error Category Enumeration

```python
class ErrorCategory(Enum):
    API_KEY_MISSING = "api_key_missing"
    PROJECT_NOT_DETECTED = "project_not_detected"
    DETECTION_FAILED = "detection_failed"
    API_TIMEOUT = "api_timeout"
    PERMISSION_DENIED = "permission_denied"
```

### Error Handling Flow

```
Exception Caught
    ↓
Classify Error → Get Category
    ↓
Get User Message → Format message
    ↓
Display to User ← Log for debugging
```

### Message Template

Each error category must have:
1. User-friendly title with emoji
2. Clear problem statement
3. 2-3 specific resolution steps
4. Expected outcome or fallback behavior

---

## Testing Strategy

### Unit Tests

- **test_classify_api_key_missing**: Verify error classification
- **test_classify_project_not_detected**: Verify project detection error
- **test_classify_detection_failed**: Verify low confidence classification
- **test_classify_api_timeout**: Verify timeout classification
- **test_classify_permission_denied**: Verify permission classification
- **test_message_api_key_missing**: Verify error message format
- **test_message_project_not_detected**: Verify error message format
- **test_message_detection_failed**: Verify error message includes confidence
- **test_message_no_jargon**: Verify no technical terms in messages
- **test_emoji_usage**: Verify correct emoji for error type

### Integration Tests

- **test_full_error_flow**: Catch exception → classify → format → display

---

## Definition of Done

- [ ] ErrorCategory enum created
- [ ] Error classification logic implemented
- [ ] User message templates created for all 5 categories
- [ ] Message formatting handles confidence scores
- [ ] All 5 AC implemented and tested
- [ ] 10+ unit tests all passing
- [ ] Zero technical jargon in user messages
- [ ] Code review approved
- [ ] Story file updated to DONE

