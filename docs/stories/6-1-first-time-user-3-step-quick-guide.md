# Story 6.1: First-Time User 3-Step Quick Guide

**Epic**: Epic 6: User Onboarding & Help System
**Priority**: High
**Acceptance Criteria**: 4
**Status**: Ready for Development

## Overview

New users executing `/pe` for the first time should see a friendly 3-step quick guide that explains the system and gets them started. After completing onboarding, the guide should not appear again, but users can replay it with `/pe-quickstart`.

## Acceptance Criteria

### AC1: Detect First-Time Use and Display Quick Guide

**Given** user executes `/pe` command for the first time
**When** system detects first-time use
**Then** system displays 3-step quick guide:

```
🚀 Welcome to Prompt Enhancement!

This system helps you enhance prompts with project-aware guidance.
Let's get started quickly:

📋 Step 1: Configure Your API Key
  Run: /pe-setup
  (Only needed once)

📊 Step 2: Run Your First Enhancement
  Run: /pe "Your prompt to enhance"

🎯 Step 3: View Enhancement Results
  System will show original, enhanced prompt and implementation steps

💡 Tip: Run /pe-help for full documentation

Press [Enter] to continue...
```

**Display Requirements:**
- Emoji indicators for visual appeal (🚀, 📋, 📊, 🎯, 💡)
- Clear step numbering (1, 2, 3)
- Concise descriptions
- Action items users can take immediately
- Pointer to help documentation

---

### AC2: Remember First-Time Setup and Don't Show Again

**Given** user completes one of the 3 steps
**When** executes `/pe` again
**Then** system:
- Does not show quick guide again
- Processes command directly
- Remembers user has seen guide

**Given** first-time setup complete
**When** system initializes configuration
**Then** system stores flag indicating user completed onboarding
- Saved in `~/.prompt-enhancement/config.yaml`
- Marked as `first_time_setup_complete: true`

**Storage Details:**
- Flag persists across sessions
- Configuration file location: `~/.prompt-enhancement/config.yaml`
- YAML key: `first_time_setup_complete`
- Type: boolean (true/false)

---

### AC3: Allow User to View Guide Again with /pe-quickstart

**Given** user wants to see guide again
**When** executes `/pe-quickstart` command
**Then** system displays full 3-step quick guide again

**Behavior:**
- Command always shows guide regardless of setup status
- Does not modify setup completion flag
- User can run multiple times
- Helps onboard new team members or refresh memory

---

### AC4: Integration with Configuration System

**Given** first-time setup complete
**When** system initializes
**Then** configuration system properly handles:
- Flag reading from config file
- Flag writing when onboarding done
- Safe defaults (assume first-time if flag missing)
- Config creation if file doesn't exist

**Config File Structure:**
```yaml
first_time_setup_complete: true
# ... other config
```

---

## Technical Requirements

### First-Time Detection

```python
class FirstTimeDetector:
    def is_first_time(self) -> bool:
        """Check if this is first-time use."""
```

### Quick Guide Display

```python
class QuickGuideDisplay:
    @staticmethod
    def show_quickstart_guide() -> str:
        """Return formatted quick guide."""

    @staticmethod
    def format_guide() -> str:
        """Format 3-step guide with emojis."""
```

### Configuration Flag

```yaml
# ~/.prompt-enhancement/config.yaml
first_time_setup_complete: false  # Initially false
```

---

## Testing Strategy

### Unit Tests

- **test_first_time_detected**: Verify detection when flag missing
- **test_guide_not_shown_after_setup**: Verify flag prevents guide
- **test_guide_displayed_on_first_run**: Verify guide shows on first execution
- **test_quickstart_always_shows_guide**: Verify /pe-quickstart works anytime
- **test_flag_stored_in_config**: Verify flag saved to config file
- **test_config_creation**: Verify config file created if missing
- **test_flag_reading**: Verify flag read correctly from config
- **test_guide_formatting**: Verify guide has all required emojis and sections

### Integration Tests

- **test_first_time_workflow**: Complete first-time user journey
- **test_flag_persistence**: Flag persists across sessions
- **test_quickstart_replays_guide**: /pe-quickstart shows full guide

---

## Definition of Done

- [ ] FirstTimeDetector class created
- [ ] QuickGuideDisplay class created
- [ ] Detection logic reads config file correctly
- [ ] Guide displays with all 3 steps and emojis
- [ ] Flag stored to config after onboarding
- [ ] /pe-quickstart command implemented
- [ ] Guide doesn't show after first-time flag set
- [ ] Safe defaults (assumes first-time if config missing)
- [ ] All 4 AC implemented and tested
- [ ] 8+ unit tests all passing
- [ ] Code review approved
- [ ] Story file updated to DONE

