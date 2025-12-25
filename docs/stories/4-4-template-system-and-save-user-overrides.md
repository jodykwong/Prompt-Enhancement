# Story 4-4: Template System and Save User Overrides

**Epic**: Epic 4 - Standards Visibility & User Control
**Status**: ready-for-dev
**Created**: 2025-12-23
**Last Updated**: 2025-12-23

---

## 📖 User Story

As a **developer**,
I want **to use predefined standard templates or save my custom standard configurations**,
So that **I can quickly switch standards between projects or reuse common configurations**.

---

## 🎯 Acceptance Criteria

### AC1: Use Predefined Templates
**Given** user wants to use template
**When** executes `/pe --template fastapi "my prompt"`
**Then** system:
- [ ] Loads predefined FastAPI template standards
- [ ] Applies these standards to enhancement
- [ ] Shows "Using fastapi template" message
- [ ] Validates template exists before applying

### AC2: Built-In Templates
**Given** predefined templates exist
**When** listing available templates
**Then** system includes:
- [ ] `fastapi` - FastAPI web framework standards
- [ ] `django` - Django web framework standards
- [ ] `flask` - Flask web framework standards
- [ ] `react` - React application standards
- [ ] `generic` - Generic defaults
- [ ] Additional language-specific templates (nodejs, python, go, etc.)

### AC3: Template Discovery
**Given** user wants to know available templates
**When** executes `/pe --template` or `/pe --list-templates`
**Then** system shows:
- [ ] All available templates
- [ ] Template description (one-liner)
- [ ] Framework/language it targets
- [ ] User-created custom templates
- [ ] Option to view template details

### AC4: Save Custom Templates
**Given** user saves custom standards
**When** creating custom template
**Then** system:
- [ ] Saves to `~/.prompt-enhancement/templates/my-template.yaml`
- [ ] Allows user to reference as `/pe --template my-template "prompt"`
- [ ] Provides template edit command
- [ ] Validates template before saving

### AC5: Template Suggestion from Override
**Given** user applies overrides in multiple requests
**When** suggesting to save as template
**Then** system:
- [ ] Detects repeated overrides
- [ ] Suggests saving override as template
- [ ] Provides `/pe-save-template my-name` command
- [ ] Asks for template name and description
- [ ] Makes saving easy (one command)

### AC6: Template Priority
**Given** template and project configuration conflict
**When** executing `/pe --template X` (project has custom config)
**Then** system:
- [ ] Prioritizes template
- [ ] Shows message: "Using my-template, overriding project configuration"
- [ ] Still allows `--override` for further customization
- [ ] Applies all three levels (template > config > override)

### AC7: Template Composition
**Given** user wants to combine template with overrides
**When** executing `/pe --template fastapi --override naming=camelCase "prompt"`
**Then** system:
- [ ] Loads template standards
- [ ] Applies overrides on top of template
- [ ] Shows: "Using fastapi template with overrides"
- [ ] Demonstrates final combined standards

### AC8: Template Management
**Given** user manages custom templates
**When** using template commands
**Then** system provides:
- [ ] `/pe-template-list` - List all templates
- [ ] `/pe-template-view my-template` - View template contents
- [ ] `/pe-template-edit my-template` - Edit template
- [ ] `/pe-template-delete my-template` - Delete template
- [ ] `/pe-template-save` - Save current config as template
- [ ] `/pe-template-reset-builtin` - Reset built-in templates

---

## 🔧 Implementation Tasks

- [ ] Create built-in templates in `src/prompt_enhancement/config/templates/`
- [ ] Implement `TemplateManager` class in `src/prompt_enhancement/config/templates.py`
- [ ] Create template loader logic
- [ ] Implement template file storage and retrieval
- [ ] Add template validation
- [ ] Create CLI commands for template management
- [ ] Create unit tests in `tests/test_config/test_templates.py`
- [ ] Create integration tests for template application

---

## 📊 Test Strategy

**Unit Tests**:
- Test loading built-in templates
- Test loading custom templates
- Test invalid template handling
- Test template validation
- Test template composition (template + override)
- Test priority logic
- Test template CRUD operations
- Test template suggestion logic

**Integration Tests**:
- End-to-end with template applied
- End-to-end with custom template
- End-to-end with template + override
- End-to-end with template + project config
- Integration with enhancement generation
- Test all template management commands

**Test Coverage Target**: >95%

---

## 📝 Dependencies

**Depends On**:
- Story 4-1: Standards Display (In Progress)
- Story 4-2: Project Configuration (In Progress)
- Story 4-3: Per-Request Override (In Progress)
- Story 2-1 through 2-9: Standards Detection (✅ DONE)

**Used By**:
- CLI integration for `/pe` command
- Help system (Story 6-3 mentions templates)

---

## 📋 Files Changed

**New Files**:
- `src/prompt_enhancement/config/templates.py` - Template management
- `src/prompt_enhancement/config/templates/` - Built-in templates directory
  - `fastapi.yaml`
  - `django.yaml`
  - `flask.yaml`
  - `react.yaml`
  - `generic.yaml`
  - `nodejs.yaml`
  - `python.yaml`
- `tests/test_config/test_templates.py` - Template tests

**Modified Files**:
- `src/prompt_enhancement/cli/parser.py` - Add template flags
- `src/prompt_enhancement/config/__init__.py` - Export template classes
- `src/prompt_enhancement/enhancement/generator.py` - Use templates
- `src/prompt_enhancement/cli/commands.py` - Add template management commands

---

## 🚀 Definition of Done

- [ ] All 8 acceptance criteria implemented
- [ ] Built-in templates created and tested
- [ ] Template management working end-to-end
- [ ] All unit tests passing (>95% coverage)
- [ ] All integration tests passing
- [ ] Code review completed
- [ ] No HIGH severity issues
- [ ] Documentation updated
- [ ] Tested in Claude Code environment
- [ ] Story marked as done in sprint-status.yaml

---

## 💬 Notes

- Keep templates simple but complete (all 5 standards defined)
- Provide helpful descriptions for each template
- Make custom template creation and discovery easy
- Consider version management for templates (optional for future)
- Built-in templates should reflect real-world frameworks
- Template directory: `~/.prompt-enhancement/templates/`
- Built-in template directory: package installation location

---
