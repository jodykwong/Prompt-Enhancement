# Story 3.3: Generate Project-Specific Implementation Steps and Verification Criteria

**Story ID**: 3.3
**Epic**: Epic 3 - Project-Aware Prompt Enhancement
**Status**: ready-for-dev
**Created**: 2025-12-19

---

## Story

As a **prompt enhancement system**,
I want **to parse LLM responses and generate project-specific implementation steps with verification criteria**,
So that **users receive actionable, project-aware guidance that follows their project's patterns and testing standards**.

---

## Acceptance Criteria

### AC1: Extract Implementation Steps from LLM Response
**Given** LLM generated an enhanced prompt with implementation guidance
**When** processing the LLM response
**Then** system:
- Parses response to identify implementation steps (Step 1, Step 2, etc., or bullet points)
- Extracts each step as independent action item
- Preserves original step numbering and ordering
- Detects step dependencies (if Step B depends on Step A, mark this)
- Handles steps in multiple formats: numbered list, bullets, prose descriptions
- Validates each step is actionable (contains verb + object)
- Groups related steps together
**And** implementation plan is structured and sequential

### AC2: Generate Project-Specific Verification Criteria
**Given** extracted implementation steps and project context available
**When** generating verification criteria
**Then** system:
- Creates specific criteria for each step (not generic checklist)
- Criteria include:
  - What artifact should exist (code file, test file, configuration, etc.)
  - Expected behavior or functionality
  - Code review checklist items (following detected standards)
  - Testing approach specific to project's test framework
  - Performance or quality gates if applicable
- Criteria follow project's naming conventions (e.g., test file naming)
- Criteria reference project's code organization pattern
- Uses project's documentation style for criteria format
**And** verification criteria are measurable and testable

### AC3: Customize Guidance by Project Type
**Given** project type detected from Epic 2
**When** generating implementation guidance
**Then** system:
- Provides different guidance for different project types (Flask vs FastAPI vs async vs sync)
- Suggests appropriate patterns for project architecture (MVC, microservices, monolithic)
- Recommends project-appropriate libraries and frameworks
- Tailors step complexity based on project maturity (new vs established)
- References existing modules/patterns in the project for consistency
- Suggests test locations based on project's test organization
**And** guidance is specifically applicable to this project, not generic

### AC4: Add Code Examples Following Detected Standards
**Given** project's detected coding standards
**When** providing code examples in implementation guidance
**Then** system:
- Generates code examples following project's naming conventions
- Examples follow detected code organization patterns
- Examples use project's detected import organization style
- Examples match project's detected docstring/comment style
- Examples follow project's detected indentation (2-space, 4-space, tabs)
- Examples reference actual dependencies found in project
- Marks examples with `[Example for {project_type}]` header
- Never shows conflicting code styles in same response
**And** code examples are directly copy-paste applicable with minimal changes

### AC5: Include Testing Guidance Specific to Framework
**Given** project's test framework detected (pytest, unittest, jest, etc.)
**When** adding testing guidance
**Then** system:
- Recommends test framework specific syntax
- Suggests test file location based on project's test organization
- Provides test structure following project's test patterns
- Includes mocking approach for project's test framework
- Recommends fixtures/setup based on framework (pytest fixtures vs unittest setUp)
- Suggests assertion style matching project's conventions
- Includes test coverage expectations
- Notes any special configuration needed (pytest.ini, test runners, etc.)
**And** testing guidance is immediately actionable with project's test framework

### AC6: Create Comprehensive Implementation Guide
**Given** extracted steps, verification criteria, examples, and testing guidance
**When** compiling final implementation guide
**Then** system:
- Organizes into logical sections (Overview, Steps, Verification, Testing, Edge Cases)
- Includes implementation timeline/order recommendations
- Notes which steps can be done in parallel
- Includes common pitfalls and how to avoid them
- Provides rollback/cleanup instructions if implementation fails
- Includes debugging tips specific to project setup
- References documentation for any frameworks/libraries used
- Includes links to relevant code in project (if available)
**And** guide provides complete implementation roadmap

### AC7: Handle Multiple Implementation Paths
**Given** some enhancements might have multiple valid implementation approaches
**When** LLM response contains alternatives
**Then** system:
- Detects when multiple approaches are suggested
- Presents each approach separately with clear headers
- Indicates trade-offs for each approach (complexity, performance, maintainability)
- Notes which approach aligns best with project's detected patterns
- Allows user to select which path to follow
- Generates verification criteria for each path
**And** users can choose most appropriate implementation path

### AC8: Validation and Quality Checks
**Given** implementation guidance generated
**When** validating completeness
**Then** system:
- Validates each step has corresponding verification criteria
- Validates code examples have correct syntax for project language
- Validates test framework references match project's framework
- Ensures no conflicting recommendations (e.g., contradictory step order)
- Validates naming examples follow project conventions
- Checks that all referenced project patterns actually exist
- Logs warnings for any unverifiable references
- Ensures guide is length-appropriate (not too brief or overwhelmingly long)
**And** generated guidance is complete and consistent

---

## Implementation Context

### Architecture Integration

**Inputs** (from Story 3.2):
- LLM response with enhanced prompt and implementation guidance
- Project context (from Story 3.1)
- Enhancement result metadata (tokens, provider, timing)

**Outputs** (for CLI display):
- Structured `ImplementationGuide` containing:
  - Implementation steps (parsed from response)
  - Verification criteria (generated)
  - Code examples (following standards)
  - Testing guidance (framework-specific)
  - Common pitfalls
  - Debugging tips

**New Modules** (to implement):
- `src/prompt_enhancement/enhancement/step_extractor.py` - Extract steps from LLM response
- `src/prompt_enhancement/enhancement/criteria_generator.py` - Generate verification criteria
- `src/prompt_enhancement/enhancement/guide_builder.py` - Compile final implementation guide

### Data Flow

```
LLM Response
    ↓
StepExtractor (AC1)
    ↓
ProjectContext + Steps
    ↓
CriteriaGenerator (AC2-AC5)
    ↓
Steps + Criteria + Examples + TestingGuidance
    ↓
GuideBuilder (AC6-AC7)
    ↓
ImplementationGuide (AC8 validation)
    ↓
Return to CLI Display Layer
```

### Testing Strategy

- Mock LLM responses with various step formats
- Test extraction of steps from prose, bullets, numbered lists
- Test criteria generation for multiple project types
- Test code example generation following standards
- Test framework-specific guidance generation
- Integration tests with Story 3.1 and 3.2 outputs
- Edge case tests: malformed responses, missing context, conflicting standards

### Performance Considerations

- Step extraction: regex-based parsing (< 100ms for typical response)
- Criteria generation: template-based with project context lookups (< 200ms)
- Code example generation: deterministic based on standards (< 150ms)
- Total Story 3.3 processing: < 500ms
- No external API calls in this story

### Backward Compatibility

- No existing code affected
- New modules are independent
- Gracefully handles missing project context (falls back to generic guidance)
- Validates all project standards exist before referencing them

---

## Dev Record

- **2025-12-19**: Story created
