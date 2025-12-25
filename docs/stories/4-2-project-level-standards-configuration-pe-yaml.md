# Story 4-2: Project-Level Standards Configuration (`.pe.yaml`)

**Epic**: Epic 4 - Standards Visibility & User Control
**Status**: ready-for-dev
**Created**: 2025-12-23
**Last Updated**: 2025-12-23

---

## 📖 User Story

As a **developer**,
I want **to set coding standards once in a project configuration file**,
So that **all subsequent `/pe` commands use these standards without reconfiguration**.

---

## 🎯 Acceptance Criteria

### AC1: Read Project Configuration File
**Given** user creates `.claude/pe-config.yaml` file
**When** `/pe` command executes
**Then** system:
- [ ] Reads project-level configuration file
- [ ] Overrides auto-detected standards
- [ ] Applies these standards to all enhancements for this project
- [ ] Shows "Using project configuration standards" message

### AC2: Parse YAML Configuration Format
**Given** configuration file contains custom standards
**When** file format is YAML
**Then** system parses:
```yaml
naming_convention: snake_case
test_framework: pytest
documentation_style: google
code_organization: by-feature
module_naming_pattern: service_
```
- [ ] Valid YAML parsing
- [ ] All 5 fields recognized
- [ ] Invalid fields handled gracefully
- [ ] Empty/missing fields use auto-detection

### AC3: Configuration Validation
**Given** configuration file contains invalid values
**When** parsing configuration
**Then** system:
- [ ] Shows friendly error message
- [ ] Suggests correct values
- [ ] Lists valid options
- [ ] Falls back to auto-detection
- [ ] Logs warning for invalid values

### AC4: Configuration Priority
**Given** project-level configuration exists
**When** conflicts with auto-detection
**Then** system:
- [ ] Prioritizes project configuration
- [ ] Logs override in debug log
- [ ] Shows "Using project configuration" message
- [ ] Does not re-detect standards

### AC5: Dynamic Configuration Reload
**Given** configuration file updated
**When** change detected
**Then** system:
- [ ] Rereads configuration
- [ ] Applies new standards
- [ ] No restart needed
- [ ] Validates new config before applying

### AC6: Configuration Locations
**Given** user wants to configure standards
**When** looking for config file
**Then** system checks locations in order:
- [ ] `.claude/pe-config.yaml` (project root)
- [ ] `.pe.yaml` (project root, fallback)
- [ ] Auto-detection if not found

### AC7: Safe Defaults
**Given** configuration file missing
**When** system initializes
**Then** system:
- [ ] Uses auto-detected standards
- [ ] Does not error on missing config
- [ ] Suggests creating config file
- [ ] Works without configuration

---

## 🔧 Implementation Tasks

- [ ] Create `ConfigLoader` class in `src/prompt_enhancement/config/loader.py`
- [ ] Implement YAML parsing with validation
- [ ] Create `ConfigSchema` for validation
- [ ] Implement configuration priority logic
- [ ] Add file watching for dynamic reload
- [ ] Create unit tests in `tests/test_config/test_loader.py`
- [ ] Create integration tests with standards detection
- [ ] Test invalid configuration handling

---

## 📊 Test Strategy

**Unit Tests**:
- Test YAML parsing for valid config
- Test invalid value detection
- Test missing/empty field handling
- Test priority logic (config vs. auto-detection)
- Test configuration file locations
- Test error messages for invalid config
- Test dynamic reload

**Integration Tests**:
- End-to-end with config file present
- End-to-end with config file missing
- End-to-end with partial config
- Integration with enhancement pipeline

**Test Coverage Target**: >95%

---

## 📝 Dependencies

**Depends On**:
- Story 2-1 through 2-9: Standards Detection (✅ DONE)
- Story 4-1: Standards Display (In Progress)

**Used By**:
- Story 4-3: Per-request override flag
- Story 4-4: Template system

---

## 📋 Files Changed

**New Files**:
- `src/prompt_enhancement/config/loader.py` - Configuration loading
- `src/prompt_enhancement/config/schema.py` - Configuration schema validation
- `tests/test_config/test_loader.py` - Config loader tests

**Modified Files**:
- `src/prompt_enhancement/config/__init__.py` - Export config classes
- `src/prompt_enhancement/enhancement/generator.py` - Load config before enhancement

---

## 🚀 Definition of Done

- [ ] All 7 acceptance criteria implemented
- [ ] Configuration loading working end-to-end
- [ ] All unit tests passing (>95% coverage)
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] No HIGH severity issues
- [ ] Documentation updated
- [ ] Tested in Claude Code environment
- [ ] Story marked as done in sprint-status.yaml

---

## 💬 Notes

- Configuration should be immutable after loading (use frozen dataclass)
- Support both `.claude/pe-config.yaml` and `.pe.yaml` locations
- Provide helpful error messages with valid value suggestions
- Log all configuration changes for debugging
- Consider environment variable overrides (optional for future)

---
