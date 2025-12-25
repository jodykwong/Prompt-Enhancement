# Story 5.3: User Confirmation of Degradation Decision

**Epic**: Epic 5: Robust Error Handling & Graceful Degradation
**Priority**: High
**Acceptance Criteria**: 4
**Status**: Ready for Development

## Overview

Before the system degrades to a lower quality level, it must ask the user for confirmation. Users should understand exactly why quality will degrade, what the degraded level provides, and have options to continue, stop, or troubleshoot.

## Acceptance Criteria

### AC1: Show Degradation Warning Before Proceeding

**Given** system detects need for degradation
**When** evaluating degradation possibility
**Then** system does NOT auto-degrade, instead:
1. Shows degradation warning
2. Explains why degradation is needed
3. Shows expected quality level
4. Asks user whether to continue

The system should pause and wait for user input before proceeding.

---

### AC2: Display Degradation Confirmation Prompt

**Given** degradation confirmation prompt displayed
**When** waiting for user input
**Then** system shows interactive prompt with 3 options:

```
⚠️ Project Detection Failed - Quality Will Degrade

System could not auto-detect project type.
Suggested degradation level: Level 3 (Generic Enhancement)

Would you like to:
[Y] Continue (Accept degraded quality)
[N] Stop (Cancel enhancement)
[T] Troubleshoot (View diagnostic info)
```

**Format Requirements:**
- Warning emoji (⚠️) for degradation
- Current degradation level explicitly shown
- 3 distinct options with clear labels
- Interactive input prompt (Y/N/T)
- Indication of what each option does

---

### AC3: Handle User's Continue Decision

**Given** user selects [Y] Continue
**When** processing their decision
**Then** system:
- Shows acknowledgment: "Continuing in degraded mode"
- Applies the corresponding degradation level
- Marks output as degraded quality
- Proceeds with enhancement

**Quality Marking Details:**
- Output should indicate "Level 2 Enhancement" or "Level 3 Enhancement"
- Recommendations shown for improving quality (create .pe.yaml, set API key, etc.)
- User understands this is degraded output, not full capability

---

### AC4: Handle User's Stop Decision

**Given** user selects [N] Stop
**When** processing their decision
**Then** system:
- Cancels the enhancement operation
- Shows message: "Enhancement cancelled"
- Performs no processing
- Exits cleanly with no errors

---

### AC5: Handle Troubleshoot Decision

**Given** user selects [T] Troubleshoot
**When** user wants diagnostic information
**Then** system shows:
- What detection was attempted (project type, standards detection, etc.)
- Detailed error reasons (e.g., "No package.json found")
- Potential fix suggestions (e.g., "Create package.json in project root")
- File paths that were checked
- Option to retry after fixes

**Example Output:**
```
📊 Diagnostic Information

Detection Attempted:
├─ Project Type: Attempted detection
│  └─ Failed: No identifying files found
├─ Standards Detection: Not attempted (no project context)
└─ API Connection: Not attempted (no project to enhance)

Potential Fixes:
1. Ensure you are in the project root directory
2. Create package.json (for Node.js projects) or requirements.txt (for Python)
3. Retry after creating identifying files

Files Checked:
- package.json (not found)
- requirements.txt (not found)
- pyproject.toml (not found)
- setup.py (not found)

Would you like to:
[R] Retry after fixing
[C] Continue anyway (degraded mode)
[N] Cancel
```

---

## Technical Requirements

### User Input Handler

```python
class DegradationConfirmation:
    @staticmethod
    def prompt_user(
        degradation_level: DegradationLevel,
        reason: str,
    ) -> UserDecision:
        """
        Show degradation confirmation prompt.
        Returns: Y (continue), N (stop), T (troubleshoot)
        """
```

### User Decision Enum

```python
class UserDecision(Enum):
    CONTINUE = "continue"
    STOP = "stop"
    TROUBLESHOOT = "troubleshoot"
    RETRY = "retry"
```

### Diagnostic Information

```python
@dataclass
class DiagnosticInfo:
    attempted_detections: List[str]
    failure_reasons: Dict[str, str]
    fix_suggestions: List[str]
    checked_files: List[str]
    missing_files: List[str]
```

---

## Testing Strategy

### Unit Tests

- **test_prompt_shows_degradation_level**: Verify correct level shown
- **test_prompt_explains_why_degrading**: Verify reason is clear
- **test_continue_decision_proceeds**: Verify [Y] continues
- **test_stop_decision_cancels**: Verify [N] cancels cleanly
- **test_troubleshoot_decision_shows_diagnostics**: Verify [T] shows diagnostics
- **test_output_marked_degraded**: Verify output indicates degradation level
- **test_recommendations_shown**: Verify quality improvement recommendations
- **test_invalid_input_reprompts**: Verify invalid input handled

### Integration Tests

- **test_full_degradation_workflow_with_confirmation**: End-to-end with user input
- **test_diagnostic_info_complete**: Verify diagnostic completeness

---

## Definition of Done

- [ ] DegradationConfirmation class created
- [ ] Interactive prompt display implemented
- [ ] Continue [Y] handling implemented
- [ ] Stop [N] handling implemented
- [ ] Troubleshoot [T] handling implemented
- [ ] Diagnostic information collection working
- [ ] Output marked with degradation level
- [ ] Recommendations shown for quality improvement
- [ ] All 4 AC implemented and tested
- [ ] 8+ unit tests all passing
- [ ] Code review approved
- [ ] Story file updated to DONE

