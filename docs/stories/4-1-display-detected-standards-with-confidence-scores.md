# Story 4-1: Display Detected Standards with Confidence Scores

**Epic**: Epic 4 - Standards Visibility & User Control
**Status**: ready-for-dev
**Created**: 2025-12-23
**Last Updated**: 2025-12-23

---

## 📖 User Story

As a **enhancement system**,
I want **to display all detected coding standards with confidence scores and evidence**,
So that **users see how the system understands their project**.

---

## 🎯 Acceptance Criteria

### AC1: Display All 5 Detected Standards
**Given** project analysis and standards detection complete
**When** displaying results
**Then** system displays all 5 standards:
- [ ] Naming convention (e.g., snake_case 90% confidence)
- [ ] Test framework (e.g., pytest 95% confidence)
- [ ] Documentation style (e.g., Google docstrings 85% confidence)
- [ ] Code organization (e.g., by-feature 80% confidence)
- [ ] Module naming (e.g., service_*.py 88% confidence)

### AC2: Include Standard Metadata
**Given** standards detected
**When** displaying information
**Then** each standard includes:
- [ ] Standard name and detected value
- [ ] Confidence score (0-100%)
- [ ] Sample size ("analyzed in 89 files")
- [ ] Concrete evidence examples
- [ ] Any exceptions noted

### AC3: Confidence-Based Formatting
**Given** high-confidence standards (>85%)
**When** displaying
**Then** marked as "High confidence"
- [ ] Clear examples provided
- [ ] Visual indicator (✓ or green)

**Given** medium-confidence standards (60-85%)
**When** displaying
**Then** marked as "Medium confidence"
- [ ] Visual indicator (▪ or yellow)
- [ ] Explanation of exceptions

**Given** low-confidence standards (<60%)
**When** displaying
**Then** marked as "Low confidence"
- [ ] Visual warning indicator (⚠ or red)
- [ ] Suggests user verification
- [ ] Provides override method

### AC4: Mixed Conventions Display
**Given** mixed conventions detected
**When** displaying results
**Then** system shows:
- [ ] Dominant convention (>60%)
- [ ] Secondary convention (20-60%)
- [ ] Exceptions explained
- [ ] Distribution percentages

### AC5: Output Formatting
**Given** results displayed
**When** formatting output
**Then** system:
- [ ] Uses plain text for terminal compatibility
- [ ] Includes emoji for visual clarity (📋, ⚡, ✓, ⚠)
- [ ] Structures for readability
- [ ] Works with screen readers
- [ ] Fits 80-character terminal width

---

## 🔧 Implementation Tasks

- [ ] Create `StandardsDisplay` class in `src/prompt_enhancement/standards/display.py`
- [ ] Implement `format_standards_report()` method
- [ ] Implement confidence score formatting logic
- [ ] Add evidence example generation
- [ ] Create unit tests in `tests/test_standards/test_display.py`
- [ ] Create integration tests for display pipeline
- [ ] Verify output formatting in terminal

---

## 📊 Test Strategy

**Unit Tests**:
- Test formatting of high-confidence standards
- Test formatting of low-confidence standards
- Test mixed convention display
- Test evidence example generation
- Test emoji and special character handling
- Test 80-character wrap handling

**Integration Tests**:
- End-to-end display with real detected standards
- Display with confidence variations
- Display with edge cases (0%, 100%, mixed)

**Test Coverage Target**: >95%

---

## 📝 Dependencies

**Depends On**:
- Story 2-9: Generate Confidence Scores (✅ DONE)
- Story 2-1 through 2-8: All Standards Detection (✅ DONE)

**Used By**:
- Story 4-2, 4-3, 4-4: All configuration stories need display

---

## 📋 Files Changed

**New Files**:
- `src/prompt_enhancement/standards/display.py` - Standards display formatting
- `tests/test_standards/test_display.py` - Display tests

**Modified Files**:
- `src/prompt_enhancement/standards/__init__.py` - Export display classes
- `src/prompt_enhancement/cli/output_formatter.py` - Integrate display output

---

## 🚀 Definition of Done

- [ ] All 5 acceptance criteria implemented
- [ ] All unit tests passing (>95% coverage)
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] No HIGH severity issues
- [ ] Documentation updated
- [ ] Tested in Claude Code environment
- [ ] Story marked as done in sprint-status.yaml

---

## 💬 Notes

- Use consistent emoji theme with Epic 1-3 (✓, ⚠, 📋, ⚡)
- Keep output concise but informative
- Provide clear override instructions in output
- Support both high and low verbosity modes

---
