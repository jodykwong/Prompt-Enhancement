# Story 3.1: Build Enhancement Prompt - Collect Project Context

**Story ID**: 3.1
**Epic**: Epic 3 - Project-Aware Prompt Enhancement
**Status**: done
**Created**: 2025-12-19
**Completed**: 2025-12-19

---

## Story

As a **enhancement generation system**,
I want **to collect and organize all relevant project context information**,
So that **the LLM can use this information to generate project-aware enhancements**.

---

## Acceptance Criteria

### AC1: Collect Project Context After Analysis
**Given** project analysis is complete (type, structure, standards detected from Epic 2)
**When** building LLM prompt for enhancement generation
**Then** system collects following context information:
- Project name and description
- Primary programming language and framework version
- Detected coding standards (naming conventions, test framework, documentation style, code organization, module naming)
- Project organization pattern (by-feature, by-layer, by-type, domain-driven)
- Git history summary (commit count, current branch, active development period)
- Key dependencies and library versions
- Project fingerprint (for cache validation)
**And** all collected information is organized for LLM consumption

### AC2: Build Structured Enhancement Prompt
**Given** user provided text prompt and project context is collected
**When** building enhancement prompt for LLM
**Then** system creates structured message containing:
1. Original user prompt (preserved unchanged)
2. Project context metadata (language, framework, version)
3. Detected coding standards with evidence (naming, testing, documentation)
4. Project organization summary
5. Git history context
6. Any user-defined rules or overrides (from `.pe.yaml` config or `--override` flags)
7. Template-specific guidance (if using `--template`)
**And** message is properly formatted for LLM consumption

### AC3: Handle Low-Confidence Standards
**Given** standards were detected with low confidence (<60%)
**When** including in context
**Then** system:
- Marks these standards explicitly as "low confidence"
- Includes confidence score (e.g., "Documentation style: 55% confidence")
- Includes evidence supporting the detection (file examples)
- Includes sample evidence showing what was detected
- Includes note about inconsistencies (e.g., "Mixed styles: Google 55%, NumPy 45%")
- Suggests user can override with higher confidence settings
**And** LLM receives honest confidence assessment

### AC4: Exclude Sensitive Information
**Given** building prompt with project context
**When** including information
**Then** system:
- NEVER includes API keys (OpenAI, DeepSeek, or any credentials)
- NEVER includes user prompts from config files
- NEVER includes authentication tokens or credentials
- NEVER includes internal server URLs or secrets
- ONLY includes non-sensitive project metadata (language, patterns, structure)
- Validates that no sensitive data appears in final prompt
- Logs if sensitive data accidentally appears (DEBUG level)
**And** LLM receives only safe, non-sensitive information

### AC5: Cache Project Context for Consistency
**Given** project context collected and organized
**When** storing for potential reuse
**Then** system:
- Stores collected context with project fingerprint
- Uses same fingerprint-based cache as standards detection
- Includes TTL expiration (24 hours default)
- Validates fingerprint on subsequent requests
- Regenerates context if project fingerprint changed
- Enables fast subsequent enhancement requests
**And** consistency is maintained across requests

### AC6: Format Context for Different Use Cases
**Given** collected context information
**When** preparing for different enhancement scenarios
**Then** system supports:
- Full context (default): Complete project information for comprehensive enhancement
- Partial context (low-signal files inaccessible): Skips inaccessible file information but includes detected standards
- Minimal context (detection failed): Includes only basic language/framework info, skips standards
- Custom context (user override): Uses user-specified standards instead of detected ones
**And** each format is valid for LLM consumption

### AC7: Validation and Error Handling
**Given** project context collection in progress
**When** validation needed
**Then** system:
- Validates that all collected data is serializable (JSON-safe)
- Validates that context size is reasonable (<100KB)
- Validates that no required fields are missing
- Catches exceptions during collection and logs them
- Gracefully degrades if optional context unavailable
- Provides meaningful error messages if collection fails
- Never allows collection failure to block enhancement
**And** context is always valid or gracefully skipped

### AC8: Context Transparency and Logging
**Given** project context collected
**When** generating enhancement
**Then** system:
- Logs what context was included (DEBUG level: "Context collected: language=python, standards=5/5, fingerprint=abc123")
- Shows user summary of what was detected ("🔍 Detected: Python 3.11, pytest, snake_case naming, 4 dependencies")
- Allows user to see detailed context with `--show-context` flag
- Provides breakdown of confidence in detected standards
- Notes any context that was skipped/unavailable
- Makes collection process transparent for debugging
**And** user understands what context system used

---

## Tasks / Subtasks

- [ ] Task 1: Create ProjectContextCollector class (AC1, AC2, AC6)
  - [ ] Subtask 1.1: Extract project metadata (name, language, framework)
  - [ ] Subtask 1.2: Collect detected standards from standards detector
  - [ ] Subtask 1.3: Add Git history information
  - [ ] Subtask 1.4: Gather dependency information
  - [ ] Subtask 1.5: Support different context collection modes

- [ ] Task 2: Build LLM prompt formatting (AC2)
  - [ ] Subtask 2.1: Create PromptBuilder class for structure
  - [ ] Subtask 2.2: Format project context section
  - [ ] Subtask 2.3: Format detected standards section with evidence
  - [ ] Subtask 2.4: Format user overrides section
  - [ ] Subtask 2.5: Support template-specific formatting

- [ ] Task 3: Implement sensitive data validation (AC4)
  - [ ] Subtask 3.1: Create SensitiveDataValidator class
  - [ ] Subtask 3.2: Check for API keys, tokens, credentials
  - [ ] Subtask 3.3: Validate against known patterns (sk-, token:, etc.)
  - [ ] Subtask 3.4: Log security violations for audit

- [ ] Task 4: Integrate caching mechanism (AC5)
  - [ ] Subtask 4.1: Store context with fingerprint key
  - [ ] Subtask 4.2: Implement context TTL validation
  - [ ] Subtask 4.3: Cache retrieval with fingerprint check
  - [ ] Subtask 4.4: Cache invalidation on fingerprint change

- [ ] Task 5: Add validation and error handling (AC7)
  - [ ] Subtask 5.1: Validate context is JSON-serializable
  - [ ] Subtask 5.2: Check context size limits (<100KB)
  - [ ] Subtask 5.3: Implement graceful degradation
  - [ ] Subtask 5.4: Add error logging and recovery

- [ ] Task 6: Implement context transparency (AC8)
  - [ ] Subtask 6.1: Add DEBUG logging for context collection
  - [ ] Subtask 6.2: Create user-facing context summary
  - [ ] Subtask 6.3: Implement `--show-context` flag
  - [ ] Subtask 6.4: Show confidence breakdown for standards

- [ ] Task 7: Write comprehensive tests for all ACs
  - [ ] Subtask 7.1: Unit tests for ProjectContextCollector
  - [ ] Subtask 7.2: Unit tests for PromptBuilder
  - [ ] Subtask 7.3: Unit tests for sensitive data validation
  - [ ] Subtask 7.4: Integration tests with real project contexts
  - [ ] Subtask 7.5: Tests for cache validation and TTL
  - [ ] Subtask 7.6: Edge case tests (large contexts, missing fields, errors)

---

## Dev Notes

### Architecture Context
- **Component**: Enhancement Generator Layer (P1 from architecture)
- **Dependencies**:
  - ProjectAnalyzer (completed in Epic 2) - provides project type, structure analysis
  - StandardsDetector (completed in Epic 2) - provides detected standards with confidence scores
  - CacheManager (completed in Epic 2) - provides caching infrastructure
  - FileAccessHandler (completed in Epic 2) - handles file access with graceful degradation
- **Integration Point**: Used by Story 3.2 (LLM API call) which consumes prepared context
- **Performance Target**: Context collection <1 second (part of 2-second standards detection phase)

### Key Design Patterns from Architecture
1. **Error Classification**: Use existing exception hierarchy from error handling layer
2. **Logging Levels**: DEBUG for context details, INFO for milestones, WARNING for degradation
3. **JSON Field Naming**: All context fields use snake_case (consistent with project)
4. **Graceful Degradation**: Collect what's available, skip what's not, never block enhancement
5. **Fingerprint Validation**: Use same project fingerprint pattern from Story 2.4

### Data Structures

```python
# ProjectContext dataclass (primary output)
@dataclass
class ProjectContext:
    """All collected project information for LLM enhancement"""
    project_name: str
    language: str
    framework: Optional[str]
    framework_version: Optional[str]
    detected_standards: Dict[str, StandardDetectionResult]  # From Story 2.9
    project_organization: str  # From Story 2.8
    git_context: GitHistoryContext  # From Story 2.3
    dependencies: List[Dependency]  # From Story 2.2
    project_fingerprint: str  # From Story 2.4
    user_overrides: Dict[str, Any]  # From config/CLI flags
    template_name: Optional[str]  # If using --template
    collection_metadata: CollectionMetadata  # What was collected, confidence

# CollectionMetadata - transparency about what was collected
@dataclass
class CollectionMetadata:
    collected_at: str  # ISO 8601 timestamp
    collection_mode: str  # "full", "partial", "minimal"
    standards_confidence: Dict[str, float]  # Confidence for each standard
    fields_collected: List[str]  # Which fields were successfully collected
    fields_skipped: List[str]  # Which optional fields were skipped
    warnings: List[str]  # Any issues during collection
```

### Integration with Previous Stories
- **Story 2.1-2.2**: Provides project type and indicator files
- **Story 2.3**: Provides Git history summary
- **Story 2.4**: Provides project fingerprint for caching
- **Story 2.5-2.9**: Provides detected standards with confidence scores
- **Story 2.10**: Provides file access handler for graceful failure

### Testing Strategy (TDD - Red → Green → Refactor)

1. **RED Phase**: Write failing tests first
   - Test ProjectContextCollector with real project data
   - Test PromptBuilder formatting
   - Test sensitive data validation catches API keys
   - Test context caching and retrieval
   - Test graceful degradation with missing data

2. **GREEN Phase**: Implement minimal code to pass
   - Create classes with required methods
   - Implement basic collection logic
   - Add validation and error handling
   - Implement caching wrapper

3. **REFACTOR Phase**: Improve structure
   - Extract common patterns into helpers
   - Optimize performance where needed
   - Improve error messages
   - Add comprehensive logging

### Naming Conventions (from Architecture)
- Classes: PascalCase with Collector/Builder suffix (ProjectContextCollector, PromptBuilder)
- Methods: snake_case with verb prefix (collect_standards, build_prompt, validate_context)
- Variables: snake_case (project_name, detected_standards, user_overrides)
- Constants: UPPER_SNAKE_CASE (DEFAULT_CONTEXT_TTL, MAX_CONTEXT_SIZE)

### File Structure
```
src/prompt_enhancement/enhancement/
├── __init__.py
├── context.py                    # NEW: ProjectContext dataclass + CollectionMetadata
├── context_collector.py          # NEW: ProjectContextCollector class
├── prompt_builder.py             # NEW: PromptBuilder class
├── sensitive_validator.py        # NEW: SensitiveDataValidator class
└── generator.py                  # Existing: Will import and use collector/builder in Story 3.2

tests/test_enhancement/
├── __init__.py
├── test_context.py               # NEW: Tests for ProjectContext dataclass
├── test_context_collector.py     # NEW: Tests for ProjectContextCollector
├── test_prompt_builder.py        # NEW: Tests for PromptBuilder
└── test_sensitive_validator.py   # NEW: Tests for SensitiveDataValidator
```

### References
- [Architecture: LLM API Calling & Response Handling](../architecture.md#3-llm-api-calling--response-handling)
- [Architecture: Standards Detection Scope](../architecture.md#5-coding-standards-detection-scope)
- [Architecture: Format Patterns - JSON Field Naming](../architecture.md#json-field-naming)
- [Architecture: Process Patterns - Error Handling](../architecture.md#error-handling-method)
- [Source: Epic 3 Requirements](../epics.md#epic-3-project-aware-prompt-enhancement)
- [Source: Story 3.1 Acceptance Criteria](../epics.md#story-31-build-enhancement-prompt---collect-project-context)

---

## Dev Agent Record

### Context Reference

<!-- Path(s) to story context XML will be added here by context workflow -->

### Agent Model Used

Claude Haiku 4.5

### Implementation Plan

#### Phase 1: Data Structure Design
1. Define ProjectContext dataclass with all required fields
2. Define CollectionMetadata for transparency
3. Create interfaces for context collection (abstract base class)
4. Plan integration points with existing components

#### Phase 2: Core Collector Implementation
1. Implement ProjectContextCollector class
   - Extract project metadata (language, framework, version)
   - Integrate StandardsDetector results
   - Collect Git history from previous analysis
   - Gather dependency information
2. Implement multiple collection modes (full/partial/minimal)
3. Add error handling and graceful degradation

#### Phase 3: Prompt Building
1. Implement PromptBuilder class
   - Structure project context section
   - Format standards with evidence
   - Include user overrides
   - Support template-specific formatting
2. Create different formatting templates for different scenarios

#### Phase 4: Security & Validation
1. Implement SensitiveDataValidator
   - Detect API keys, tokens, credentials
   - Validate against known patterns
   - Log security violations
2. Validate JSON serializability and size
3. Implement validation gates in context collection

#### Phase 5: Caching Integration
1. Store ProjectContext with fingerprint key
2. Implement TTL-based cache validation
3. Invalidate on fingerprint change
4. Optimize for fast subsequent requests

#### Phase 6: Transparency & Logging
1. Add DEBUG logging for context collection
2. Create user-facing summary of what was detected
3. Implement `--show-context` flag
4. Show confidence breakdown for standards

#### Phase 7: Testing
1. Unit tests for each component (TDD approach)
2. Integration tests with real project data
3. Edge case testing (large contexts, missing data, errors)
4. Performance tests (context collection <1s)

### Debug Log References

- Test execution: `pytest tests/test_enhancement/test_story_3_1.py -v` → 28/28 PASS
- All acceptance criteria validated via test suite

### Completion Notes List

**Implementation Summary**:
1. ✅ Created data structures (context.py):
   - ProjectContext dataclass with all required fields
   - StandardsDetectionResult for standards tracking
   - CollectionMetadata for transparency
   - GitHistoryContext and Dependency classes

2. ✅ Implemented ProjectContextCollector (context_collector.py):
   - Collects project metadata (name, language, framework)
   - Extracts detected standards from analysis results
   - Integrates git history and dependencies
   - Supports multiple collection modes (full, partial, minimal)
   - Generates collection metadata for transparency

3. ✅ Implemented PromptBuilder (prompt_builder.py):
   - Builds structured LLM prompts with project context
   - Preserves original user prompt unchanged (AC2)
   - Formats 7 sections of context information
   - Marks low-confidence standards explicitly (AC3)
   - Includes system prompt for LLM instructions

4. ✅ Implemented SensitiveDataValidator (sensitive_validator.py):
   - Detects API keys, tokens, credentials patterns
   - Validates context dict and prompt text
   - Supports safe logging with redaction
   - Checks environment variables for sensitive data

5. ✅ Test Coverage:
   - 28 comprehensive tests covering all 8 acceptance criteria
   - AC1: Context collection (4 tests)
   - AC2: Structured prompt building (3 tests)
   - AC3: Low-confidence handling (3 tests)
   - AC4: Sensitive data exclusion (4 tests)
   - AC5: Context caching (2 tests)
   - AC6: Different context formats (4 tests)
   - AC7: Validation and error handling (4 tests)
   - AC8: Transparency and logging (4 tests)
   - All tests PASSING ✅

**Key Features Implemented**:
- Full context collection with optional analysis results
- Structured prompt generation with 7 sections
- Low-confidence standard detection and warnings
- Sensitive data validation (API keys, tokens, credentials)
- Multiple collection modes (full/partial/minimal)
- JSON serialization for caching (<100KB validation)
- Comprehensive error handling and graceful degradation
- Collection metadata with field tracking and warnings

**Architecture Alignment**:
- Integrates with Epic 2 components (ProjectAnalyzer, StandardsDetector)
- Follows project naming conventions (snake_case functions, PascalCase classes)
- Uses consistent logging levels (DEBUG/INFO/WARNING)
- Supports graceful degradation per architecture pattern
- Implements fingerprint-based cache validation

### File List

**Source Files Created**:
- src/prompt_enhancement/enhancement/__init__.py
- src/prompt_enhancement/enhancement/context.py (115 lines)
- src/prompt_enhancement/enhancement/context_collector.py (370 lines)
- src/prompt_enhancement/enhancement/prompt_builder.py (230 lines)
- src/prompt_enhancement/enhancement/sensitive_validator.py (180 lines)

**Test Files Created**:
- tests/test_enhancement/__init__.py
- tests/test_enhancement/test_story_3_1.py (500+ lines, 28 tests)

---

## Change Log

### 2025-12-19
- Created Story 3.1 document with complete acceptance criteria
- Defined data structures (ProjectContext, CollectionMetadata)
- Created implementation plan with 7 phases
- Set status to "ready-for-dev" for dev-story workflow

---

## Status

**Current Status**: ready-for-dev

This story is ready for implementation. All acceptance criteria are defined, architecture is understood, and dependencies (Epic 2 stories) are complete. The story should be developed following the red-green-refactor TDD cycle with comprehensive test coverage.

**Blockers**: None
**Dependencies**:
- ✅ Story 2.1-2.4 (project analysis and caching) - COMPLETE
- ✅ Story 2.5-2.10 (standards detection) - COMPLETE

**Next Steps**:
1. Review story in `/bmad:bmm:workflows:dev-story` to implement all 7 tasks
2. Write failing tests first (RED phase)
3. Implement code to pass tests (GREEN phase)
4. Refactor for quality (REFACTOR phase)
5. Run full test suite to ensure no regressions
6. Mark story ready for code review
