# Story 4-3: Per-Request Override (`--override` flag)

**Epic**: Epic 4 - Standards Visibility & User Control
**Status**: ready-for-dev
**Created**: 2025-12-23
**Last Updated**: 2025-12-23

---

## 📖 User Story

As a **developer**,
I want **to temporarily override specific standards in a single `/pe` command**,
So that **I can experiment with different conventions without modifying project configuration**.

---

## 🎯 Acceptance Criteria

### AC1: Parse Override Flags
**Given** user executes `/pe` command
**When** includes `--override` flag
**Then** system parses override parameters:
- [ ] `--override naming=camelCase`
- [ ] `--override test_framework=jest`
- [ ] `--override documentation=jsdoc`
- [ ] Supports multiple overrides: `--override naming=camelCase --override test_framework=jest`
- [ ] Handles spaces and special characters

### AC2: Apply Overrides to Enhancement
**Given** override flag provided
**When** generating enhancement
**Then** system:
- [ ] Uses override value instead of detected/configured value
- [ ] Shows "Using overridden standards" message
- [ ] Applies override only to this request
- [ ] Does not modify project configuration
- [ ] Validates override before applying

### AC3: Validate Override Values
**Given** invalid override value provided
**When** parsing parameters
**Then** system:
- [ ] Shows list of valid values
- [ ] Example: `--override naming=[snake_case|camelCase|PascalCase|kebab-case]`
- [ ] Falls back to detected/configured value
- [ ] Shows helpful error message
- [ ] Does not fail the enhancement

### AC4: Handle Multiple Overrides for Same Standard
**Given** multiple overrides same standard
**When** conflicting values provided
**Then** system:
- [ ] Uses last value
- [ ] Shows warning about override
- [ ] Logs warning for debugging
- [ ] Continues with last specified value

### AC5: Override Priority
**Given** override flag used with project config
**When** both override and config exist
**Then** system applies priority:
1. [ ] Command-line `--override` flag (highest priority)
2. [ ] Project config (`.pe.yaml`)
3. [ ] Auto-detected standards (lowest priority)
- [ ] Shows which standards are active and why

### AC6: Non-Invasive Experimentation
**Given** user wants to experiment with standards
**When** using override
**Then** system:
- [ ] Does not save override to project configuration
- [ ] Applies only to current request
- [ ] Provides clear feedback about what's in use
- [ ] Makes reverting simple (just don't use override)

### AC7: Override Discovery
**Given** user wants to know available overrides
**When** using `--help` or `--override help`
**Then** system shows:
- [ ] All available override options
- [ ] Valid values for each
- [ ] Examples of usage
- [ ] Current values (detected/configured)

---

## 🔧 Implementation Tasks

- [ ] Update CLI parser in `src/prompt_enhancement/cli/parser.py`
- [ ] Add `--override` flag parsing logic
- [ ] Create override validation in config module
- [ ] Implement override merging logic
- [ ] Update `EnhancementGenerator` to use overrides
- [ ] Add override tracking and logging
- [ ] Create unit tests in `tests/test_cli/test_parser.py`
- [ ] Create integration tests for override behavior

---

## 📊 Test Strategy

**Unit Tests**:
- Test parsing single override
- Test parsing multiple overrides
- Test invalid override values
- Test override value validation
- Test multiple overrides for same standard
- Test override help/discovery
- Test empty override

**Integration Tests**:
- End-to-end with override applied
- End-to-end with project config + override
- End-to-end with invalid override
- Verify override doesn't modify config
- Verify enhancement uses override values

**Test Coverage Target**: >95%

---

## 📝 Dependencies

**Depends On**:
- Story 4-1: Standards Display (In Progress)
- Story 4-2: Project Configuration (In Progress)
- Story 2-1 through 2-9: Standards Detection (✅ DONE)

**Used By**:
- Story 4-4: Template system (can combine templates with overrides)
- CLI integration for `/pe` command

---

## 📋 Files Changed

**Modified Files**:
- `src/prompt_enhancement/cli/parser.py` - Add override flag parsing
- `src/prompt_enhancement/config/loader.py` - Add override validation
- `src/prompt_enhancement/enhancement/generator.py` - Use overrides
- `tests/test_cli/test_parser.py` - Add override parsing tests
- `tests/test_enhancement/test_generator.py` - Add override behavior tests

---

## 🚀 Definition of Done

- [ ] All 7 acceptance criteria implemented
- [ ] Override parsing working end-to-end
- [ ] All unit tests passing (>95% coverage)
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] No HIGH severity issues
- [ ] Documentation updated
- [ ] Tested in Claude Code environment
- [ ] Story marked as done in sprint-status.yaml

---

## 💬 Notes

- Keep override syntax consistent with existing CLIs (Docker, Kubernetes)
- Provide clear error messages for invalid overrides
- Log all overrides used (for auditing and debugging)
- Support both `--override key=value` and alternative syntaxes if helpful
- Ensure overrides are never persisted to config files

---
