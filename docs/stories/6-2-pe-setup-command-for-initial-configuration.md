# Story 6.2: `/pe-setup` Command for Initial Configuration

**Epic**: Epic 6: User Onboarding & Help System
**Priority**: High
**Acceptance Criteria**: 5
**Status**: Ready for Development

## Overview

New users should be able to run `/pe-setup` to interactively configure their API key and project preferences through a friendly wizard, without needing to manually edit config files.

## Acceptance Criteria

### AC1: Interactive Setup Wizard Flow

**Given** user runs `/pe-setup` command
**When** initializing setup flow
**Then** system displays interactive questionnaire with 3 steps:

**Step 1: API Key Configuration**
- Prompt for OpenAI API key
- Input masked (don't show key on screen)
- Validation with API test call
- Success message: "✓ API key valid"
- Error message with help link if invalid

**Step 2: Project Type Detection**
- Auto-detect project type (if possible)
- Show detected type and ask for confirmation
- Allow override if incorrect

**Step 3: Standards Preferences**
- Ask for naming convention
- Ask for test framework
- Both optional, can skip

**Final Message:**
- "✅ Setup Complete!"
- Suggest next step: `/pe-help`

---

### AC2: API Key Validation

**Given** user enters API key
**When** validating key
**Then** system:

**For Valid Keys:**
- Tests key with OpenAI API (simple call)
- Shows "✓ API key valid"
- Saves to `~/.prompt-enhancement/config.yaml`

**For Invalid Keys:**
- Shows "❌ API key invalid"
- Provides reason (e.g., "Invalid format" or "API rejected")
- Allows re-entry
- Provides help link: https://platform.openai.com/api-keys

**Invalid Cases:**
- Empty key
- Wrong format (not sk-...)
- API rejects the key
- API call timeout

---

### AC3: Project Type Detection

**Given** system analyzes project
**When** suggesting project type
**Then** system:
- Detects from file presence (package.json, requirements.txt, etc.)
- Asks user to confirm: "Is this correct? [Y/n]"
- Allows override with other options
- Uses detected type as default

**Detection Logic:**
- Python: requirements.txt, setup.py, pyproject.toml
- Node.js: package.json
- Java: pom.xml, build.gradle
- Go: go.mod
- Ruby: Gemfile
- Generic: No identifying files

---

### AC4: Settings Save and Skip Functionality

**Given** setup complete
**When** user confirms
**Then** system:
- Saves all settings to `~/.prompt-enhancement/config.yaml`
- Shows "✅ Setup Complete"
- Suggests next step: `/pe-help`

**Given** user wants to skip a step
**When** presses [Enter] or types "skip"
**Then** system:
- Skips that step
- Uses defaults or auto-detection
- Continues to next step

**Skipping Behavior:**
- Step 1 (API Key): Cannot skip - required
- Step 2 (Project Type): Can skip - uses detection or generic
- Step 3 (Standards): Can skip - uses defaults

---

### AC5: Interactive Questionnaire Display

**Example Output:**
```
🔧 Prompt Enhancement Setup Wizard

Step 1/3: API Key Configuration
Please enter your OpenAI API key:
[sk-...]

Successfully configured! ✓

Step 2/3: Project Type Detection
Detected project type: Python
Is this correct? [Y/n] Y

Step 3/3: Standards Preferences
Naming convention (snake_case/camelCase/other): [snake_case]
Test framework (pytest/unittest/jest/other): [pytest]

✅ Setup Complete!
You can now run: /pe "your prompt"

💡 Tip: Run /pe-help for full documentation
```

---

## Technical Requirements

### Setup Wizard Class

```python
class SetupWizard:
    def run_interactive_setup(self) -> bool:
        """Run complete setup flow."""

    def step_1_api_key(self) -> str:
        """Get and validate API key."""

    def step_2_project_type(self) -> str:
        """Detect and confirm project type."""

    def step_3_standards(self) -> Dict[str, str]:
        """Get standards preferences."""
```

### API Key Validation

```python
class APIKeyValidator:
    @staticmethod
    def validate_key(api_key: str) -> Tuple[bool, str]:
        """
        Validate API key.
        Returns: (is_valid, message)
        """
```

### Config Integration

```python
# Save to ~/.prompt-enhancement/config.yaml
setup_config = {
    "api_key": "sk-...",
    "project_type": "python",
    "naming_convention": "snake_case",
    "test_framework": "pytest",
}
```

---

## Testing Strategy

### Unit Tests

- **test_setup_wizard_initialization**: Wizard starts correctly
- **test_api_key_validation_valid**: Valid key accepted
- **test_api_key_validation_invalid**: Invalid key rejected
- **test_api_key_validation_empty**: Empty key rejected
- **test_api_key_validation_wrong_format**: Format validation works
- **test_project_type_detection_python**: Detects Python projects
- **test_project_type_detection_nodejs**: Detects Node.js projects
- **test_project_type_detection_generic**: Handles undetected projects
- **test_standards_preferences_saved**: Preferences saved to config
- **test_skip_step_functionality**: Skip works correctly
- **test_setup_config_file_created**: Config file created
- **test_setup_complete_message**: Completion message shown

### Integration Tests

- **test_full_setup_workflow**: Complete setup flow end-to-end
- **test_setup_with_skip**: Setup with skipped steps
- **test_setup_config_persistence**: Settings persist after setup
- **test_api_key_validation_with_timeout**: Timeout handling

---

## Definition of Done

- [ ] SetupWizard class created with interactive flow
- [ ] API key validation against OpenAI API
- [ ] Project type detection implemented
- [ ] Standards preferences collection
- [ ] Config file creation and saving
- [ ] Skip functionality for optional steps
- [ ] Error handling with helpful messages
- [ ] Help links for getting API keys
- [ ] All 5 AC implemented and tested
- [ ] 12+ unit tests all passing
- [ ] Code review approved
- [ ] Story file updated to DONE

