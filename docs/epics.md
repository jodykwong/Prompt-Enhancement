---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "docs/prd.md"
  - "docs/architecture.md"
workflowType: 'epics-stories'
lastStep: 4
workflowStatus: "completed"
project_name: 'Prompt-Enhancement'
user_name: 'Jodykwong'
date: '2025-12-16'
requirementsVerified: true
requirementCounts:
  functionalRequirements: 54
  nonFunctionalRequirements: 29
  technicalRequirements: "architecture-patterns"
epicCount: 6
epicsApproved: true
epicsApprovedDate: "2025-12-16T00:15:00Z"
storyCount: 28
storiesCreated: true
storiesCreatedDate: "2025-12-16T00:45:00Z"
validationCompleted: true
validationCompletedDate: "2025-12-16T01:00:00Z"
validationResults:
  frCoverage: "100% (54/54)"
  nfrCoverage: "100% (29/29)"
  storyQuality: "Excellent"
  archComplianceence: "100%"
  dependencyCheck: "All forward dependencies"
---

# Prompt-Enhancement - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for Prompt-Enhancement v1.1, decomposing the requirements from the PRD and Architecture into implementable stories organized by user value.

## Requirements Inventory

### Functional Requirements

**FR1. Command Integration & Execution (6 requirements)**
- FR1.1: Users can execute `/pe "prompt text"` command in Claude Code to enhance their prompts
- FR1.2: System automatically detects current working directory from Claude Code environment
- FR1.3: Users can optionally specify context modifiers (e.g., `--override`, `--template`, `--type`) to influence enhancement behavior
- FR1.4: System returns enhancement results within 5-15 seconds or provides clear error messages
- FR1.5: Results display original prompt, enhanced prompt, and implementation steps in Display-Only mode (not auto-executed)
- FR1.6: System streams progress updates during analysis ("Analyzing project...", "Detecting standards...", "Preparing enhancement...")

**FR2. Automatic Project Detection (6 requirements)**
- FR2.1: System automatically detects project type (Python, Node.js, Go, Rust, Java, C#, etc.) from filesystem markers
- FR2.2: System identifies project indicator files (package.json, requirements.txt, go.mod, Cargo.toml, .csproj, pom.xml, etc.)
- FR2.3: System reads Git history to extract project context (commit count, branch structure, recent changes)
- FR2.4: System gracefully handles projects not in Git repositories by skipping git analysis
- FR2.5: System identifies files and paths inaccessible due to Claude Code sandbox restrictions and skips them
- FR2.6: System generates project fingerprint (hash of package files + git log count) for caching and consistency

**FR3. Coding Standards Detection (8 requirements)**
- FR3.1: System detects project naming conventions (snake_case, camelCase, PascalCase, kebab-case) across codebase
- FR3.2: System detects project test framework (pytest, unittest, jest, mocha, NUnit, xUnit, etc.)
- FR3.3: System detects documentation style (Google docstring, NumPy style, Sphinx, JSDoc, etc.)
- FR3.4: System detects code organization patterns (by feature, by layer, by type)
- FR3.5: System generates confidence score (0-100%) for each detected standard
- FR3.6: System identifies mixed convention scenarios and reports "dominant convention" (>60%) and "secondary convention" (20-60%)
- FR3.7: System distinguishes between auto-generated code, third-party libraries, and self-written code when detecting standards
- FR3.8: System analyzes 50-100+ representative files to ensure statistical validity of detection

**FR4. Prompt Enhancement Generation (6 requirements)**
- FR4.1: System sends project context and detected standards to LLM for prompt enhancement
- FR4.2: Enhanced prompt preserves original user intent while adding project-aware guidance
- FR4.3: Enhanced prompt includes specific implementation steps tailored to project architecture
- FR4.4: Enhanced prompt includes verification criteria and testing guidance
- FR4.5: Enhanced prompt incorporates detected coding standards into recommendations
- FR4.6: System streams enhancement results progressively rather than waiting for completion

**FR5. Standards Feedback & Customization (6 requirements)**
- FR5.1: System displays all detected coding standards with confidence scores and evidence
- FR5.2: Users can confirm detected standards or provide quick overrides via single-click action
- FR5.3: Users can customize standards at project level via `.pe.yaml` or `.claude/pe-config.yaml` file
- FR5.4: Users can override standards per request using `--override` flag (e.g., `--override naming=camelCase`)
- FR5.5: System saves user standard overrides to improve future detection accuracy
- FR5.6: System supports template-based standard presets (e.g., `--template fastapi`)

**FR6. Error Handling & Graceful Degradation (7 requirements)**
- FR6.1: System classifies errors into categories: API key missing, project detection failed, standards detection low confidence, API timeout, permission denied
- FR6.2: System provides specific user guidance for each error type (e.g., "Run /pe-setup to configure API keys")
- FR6.3: When project detection fails, system degrades to generic enhancement without project context
- FR6.4: When API timeout occurs, system uses cached standards if available or quick response path
- FR6.5: When standards confidence is <60%, system displays warning but continues with low-confidence standards
- FR6.6: System provides user-friendly error messages (non-technical language) with resolution steps
- FR6.7: System implements three degradation levels: (1) Full enhancement with standards, (2) Enhancement without standards, (3) Generic enhancement only

**FR7. Onboarding & Help (5 requirements)**
- FR7.1: First-time users see 3-step quick guide when executing `/pe` command
- FR7.2: System provides `/pe-setup` command for initial configuration (API keys, project type, standards preferences)
- FR7.3: System provides `/pe-help` command showing complete documentation, examples, and advanced options
- FR7.4: System can auto-generate project-specific enhancement template suggestions based on detected tech stack
- FR7.5: System provides example enhancements for common scenarios to help users understand value

**FR8. Performance & Consistency (6 requirements)**
- FR8.1: System achieves 5-15 second response time in 95th percentile in actual Claude Code environment
- FR8.2: System caches detected standards using project fingerprint with 24-hour TTL
- FR8.3: System uses deterministic sampling (alphabetical order) to ensure consistent detection results across multiple runs
- FR8.4: System validates project fingerprint before using cached standards; re-analyzes if project changed
- FR8.5: Individual analysis phases complete within phase timeouts: context collection (5s), API call (30s), result formatting (5s)
- FR8.6: Hard timeout of 60 seconds for entire `/pe` execution respects Claude Code command limits

**FR9. Claude Code Sandbox Compatibility (4 requirements)**
- FR9.1: System successfully operates within Claude Code sandbox environment with file access restrictions
- FR9.2: System correctly resolves API key from multiple sources: project config, user config, environment variables
- FR9.3: System handles missing permissions gracefully and analyzes only accessible files
- FR9.4: System detects and handles special environment variables specific to Claude Code context

### NonFunctional Requirements

**NFR1. Performance (5 requirements)**
- NFR1.1: System response time shall be 5-15 seconds for the 95th percentile of requests in actual Claude Code environment
- NFR1.2: Project context analysis (P0.1-P0.3) shall complete within 5 seconds
- NFR1.3: LLM API call shall timeout after 30 seconds with graceful fallback
- NFR1.4: Result formatting and display shall complete within 5 seconds
- NFR1.5: System shall not exceed 60-second hard timeout imposed by Claude Code command execution

**NFR2. Integration (4 requirements)**
- NFR2.1: System shall integrate seamlessly with Claude Code `/pe` slash command interface
- NFR2.2: System shall call LLM API with batched requests (multiple analyses in single request, not individual calls)
- NFR2.3: System shall support multiple LLM providers (OpenAI primary, DeepSeek fallback) with provider-agnostic abstraction
- NFR2.4: System shall read from project Git repository without modifying it (read-only operations)

**NFR3. Reliability (5 requirements)**
- NFR3.1: System shall have zero crashes in Claude Code sandbox environment during MVP launch
- NFR3.2: System shall gracefully degrade to generic enhancement if project detection fails
- NFR3.3: System shall retry failed API calls up to 2 times before displaying error to user
- NFR3.4: System shall use cached standards if LLM API times out, providing partial value despite upstream failure
- NFR3.5: System shall handle file permission errors by skipping inaccessible paths and continuing analysis

**NFR4. Compatibility (4 requirements)**
- NFR4.1: System shall support Python, JavaScript/Node.js, Go, Rust, and Java projects in MVP
- NFR4.2: System shall function correctly in Claude Code sandbox environment with file access restrictions
- NFR4.3: System shall work across Windows, macOS, and Linux environments via Python runtime
- NFR4.4: System shall support both Git-tracked projects and non-Git projects

**NFR5. Security (4 requirements)**
- NFR5.1: System shall never log or display API keys in error messages, debug output, or user-facing text
- NFR5.2: System shall resolve API keys from sources in priority order: project config → user config → environment variables → error if not found
- NFR5.3: System shall validate API key format and availability before attempting LLM calls
- NFR5.4: System shall not cache, persist, or transmit user prompts or enhancement results to external services

**NFR6. Maintainability (4 requirements)**
- NFR6.1: Code shall be organized into modular components (P0.1-P0.5 analyzers) that can evolve independently
- NFR6.2: System shall support adding new programming language detection without refactoring core analysis pipeline
- NFR6.3: Error conditions shall be categorized and documented to enable future improvements and monitoring
- NFR6.4: System shall include logging for analysis steps (without exposing sensitive data) to aid debugging

**NFR7. Accessibility (3 requirements)**
- NFR7.1: All user-facing error messages shall use plain language, avoiding technical jargon and internal error codes
- NFR7.2: System output shall be plain-text and structured for readability by screen readers and text-based tools
- NFR7.3: Progress messages shall be clear and actionable for users without technical background

### Additional Requirements

**Technical Architecture Requirements (from Architecture Document):**

**Architectural Patterns & Consistency Rules:**
- Naming conventions: Functions (snake_case), Classes (PascalCase), Variables (snake_case), Constants (UPPER_SNAKE_CASE), Modules (snake_case)
- Structure patterns: Test files mirror `src/` structure with `test_` prefix; configuration in `config/` module; logging in `~/.prompt-enhancement/logs/`; cache in `.claude/pe-cache/`
- Format patterns: Error responses use structured Exception classes with category field; dates use ISO 8601 format; JSON uses snake_case fields
- Communication patterns: Progress messages use emoji symbols (🔍, 📊, 🚀, ⚡, ✓, ⚠️, ❌); error messages follow user-friendly format with recovery options
- Process patterns: Error handling raises exceptions in analysis modules, caught in CLI; API retries (2x, no delay); file access retries (1x, 100ms delay); cache validation uses fingerprint + TTL

**Architectural Boundaries:**
1. CLI Layer: `/pe` command handler and parameter parsing
2. Analysis Pipeline: Async orchestration of P0.1-P0.3 (tech stack, project structure, git history)
3. Standards Detection: File sampling and 5 standard categories detection (naming, testing, documentation, organization, module naming)
4. Cache Management: 3-tier caching (memory + file + optional Redis) with fingerprint validation
5. Enhancement Generation: LLM provider abstraction (OpenAI, DeepSeek, extensible)
6. Error Handling: 5-category error classification with 3-level graceful degradation
7. Configuration Management: 3-layer config loading (environment → user config → project-specific)

**Project Structure & Modular Organization:**
- `src/prompt_enhancement/cli/` - Command handling (pe_command.py, parser.py, output_formatter.py)
- `src/prompt_enhancement/pipeline/` - Analysis orchestration (analyzer.py, tech_stack.py, project_structure.py, git_history.py, context_collector.py)
- `src/prompt_enhancement/standards/` - Standards detection (detector.py, naming.py, testing.py, documentation.py, organization.py, modules.py, confidence.py, sampler.py)
- `src/prompt_enhancement/enhancement/` - LLM integration (generator.py, llm_provider.py, openai_provider.py, deepseek_provider.py, prompt_builder.py)
- `src/prompt_enhancement/cache/` - Cache management (manager.py, fingerprint.py, memory.py, persistent.py)
- `src/prompt_enhancement/error/` - Error handling (exceptions.py, classifier.py, messages.py, recovery.py, logger.py)
- `src/prompt_enhancement/config/` - Configuration (loader.py, schema.py, defaults.py)
- `src/prompt_enhancement/utils/` - Shared utilities (file_utils.py, time_utils.py, display_utils.py, constants.py)
- `tests/` - Full test mirror of src/ structure

### FR Coverage Map

| FR | Epic | Description |
|----|------|-------------|
| FR1.1-FR1.6 | Epic 1 | `/pe` command execution with progress display |
| FR2.1-FR2.6 | Epic 2 | Automatic project type, structure, and Git analysis |
| FR3.1-FR3.8 | Epic 2 | Coding standards detection with confidence scoring |
| FR4.1-FR4.6 | Epic 3 | Project-aware prompt enhancement generation |
| FR5.1-FR5.6 | Epic 4 | Standards display and multi-level customization |
| FR6.1-FR6.7 | Epic 5 | Error classification and graceful degradation |
| FR7.1-FR7.5 | Epic 6 | Onboarding, setup, and help system |
| FR8.1-FR8.6 | Epic 1, 2 | Performance targets and caching strategy |
| FR9.1-FR9.4 | Epic 2 | Claude Code sandbox compatibility |

**All 54 FRs mapped. No gaps or duplicates. ✓**

## Epic List

### Epic 1: Fast & Responsive `/pe` Command
Users can execute the /pe command and receive enhancement results in 5-15 seconds with clear progress feedback, enabling rapid iteration without context-switching delays.

**User Outcome:** Developers stay in creative flow with fast feedback loops

**FRs covered:** FR1.1, FR1.2, FR1.3, FR1.4, FR1.5, FR1.6, FR8.1-FR8.6

**Key Capabilities:**
- Execute `/pe "prompt text"` with optional context modifiers
- Real-time progress messages (🔍 Analyzing, 🚀 Enhancing, ✓ Complete)
- 5-15 second response time in Claude Code environment
- Display-Only mode for safe review before execution
- Deterministic caching for consistency

---

### Epic 2: Automatic Project & Standards Analysis
System automatically detects project type, structure, Git history, and coding conventions without user intervention, creating a "just understands my project" experience.

**User Outcome:** System learns project context automatically with full transparency

**FRs covered:** FR2.1, FR2.2, FR2.3, FR2.4, FR2.5, FR2.6, FR3.1-FR3.8, FR9.1-FR9.4

**Key Capabilities:**
- Auto-detect project type (Python, Node.js, Go, Rust, Java, C#, etc.)
- Identify project indicator files and Git history
- Detect 5 coding standards with confidence scores:
  - Naming conventions (snake_case, camelCase, PascalCase, kebab-case)
  - Test frameworks (pytest, unittest, jest, mocha, NUnit, xUnit)
  - Documentation style (Google, NumPy, Sphinx, JSDoc)
  - Code organization (by-feature, by-layer, by-type)
  - Module naming patterns
- Handle Claude Code sandbox restrictions gracefully
- Generate project fingerprint for cache validation

---

### Epic 3: Project-Aware Prompt Enhancement
LLM uses detected project context to generate enhancements that respect project conventions, architecture patterns, and include implementation steps specific to the project.

**User Outcome:** Enhancements are tailored to the specific project, not generic

**FRs covered:** FR4.1, FR4.2, FR4.3, FR4.4, FR4.5, FR4.6

**Key Capabilities:**
- Send project context to LLM with detected standards
- Generate enhancements that preserve original intent
- Include project-specific implementation steps
- Add verification criteria tailored to project architecture
- Incorporate detected standards into recommendations
- Stream results progressively for perceived speed

---

### Epic 4: Standards Visibility & User Control
System displays detected standards with confidence scores and evidence, allowing users to customize at three levels (global project, per-request, template-based).

**User Outcome:** Full transparency and multi-level control over standards detection

**FRs covered:** FR5.1, FR5.2, FR5.3, FR5.4, FR5.5, FR5.6

**Key Capabilities:**
- Display detected standards with confidence scores and evidence
- Quick override action (confirm, adjust, or customize)
- Project-level config via `.pe.yaml` or `.claude/pe-config.yaml`
- Per-request overrides using `--override naming=camelCase` flag
- Template-based presets (e.g., `--template fastapi`)
- Save overrides to improve consistency

---

### Epic 5: Robust Error Handling & Graceful Degradation
System gracefully handles failures with 5-category error classification, user-friendly messages, and 3-level degradation strategy to maintain value even when constraints encountered.

**User Outcome:** System remains helpful and guides recovery even when things go wrong

**FRs covered:** FR6.1, FR6.2, FR6.3, FR6.4, FR6.5, FR6.6, FR6.7

**Key Capabilities:**
- Classify errors: API key missing, project detection failed, low confidence, API timeout, permission denied
- Provide specific recovery guidance for each error type
- Three degradation levels: (1) Full enhancement, (2) Enhancement without standards, (3) Generic enhancement
- Display quality warnings when degraded
- User-friendly error messages without technical jargon
- User confirmation before proceeding with degraded results

---

### Epic 6: User Onboarding & Help System
New users can quickly learn and configure the system through 3-step quick guide, setup command, comprehensive help, and auto-generated template suggestions.

**User Outcome:** First-time users are productive immediately with minimal setup

**FRs covered:** FR7.1, FR7.2, FR7.3, FR7.4, FR7.5

**Key Capabilities:**
- 3-step quick guide for first-time users
- `/pe-setup` command for initial configuration (API keys, project type, standards preferences)
- `/pe-help` command with documentation, examples, and advanced options
- Auto-generate template suggestions based on detected tech stack
- Example enhancements showing system value

---

### Summary by Epic

| Epic | User Value | FRs | Key Benefit |
|------|-----------|-----|------------|
| **Epic 1** | Fast feedback loops | 10 | 5-15s response enables real-time iteration |
| **Epic 2** | Project understanding | 14 | System understands project automatically |
| **Epic 3** | Relevant suggestions | 6 | Enhancements fit the specific project |
| **Epic 4** | Full user control | 6 | Transparent with multi-level customization |
| **Epic 5** | Resilience | 7 | Graceful handling of failures |
| **Epic 6** | Easy adoption | 5 | Developers are productive immediately |
| **TOTAL** | | 54 | Complete MVP implementation |

---

---

## Epic 1: Fast & Responsive `/pe` Command

Users can execute the /pe command and receive enhancement results in 5-15 seconds with clear progress feedback, enabling rapid iteration without context-switching delays.

### Story 1.1: Execute `/pe` Command with Basic Parameter Parsing

As a **developer using Claude Code**,
I want **to execute `/pe "my prompt"` and have the system parse my input**,
So that **I can start the enhancement process with a simple command**.

**Acceptance Criteria:**

**Given** I am in Claude Code environment
**When** I type `/pe "Please help me write better error handling"`
**Then** the system parses the command and extracts the prompt text
**And** the system detects the current working directory from Claude Code
**And** the system returns an acknowledgment that processing started

**Given** I use context modifiers
**When** I type `/pe --override naming=camelCase "my prompt"`
**Then** the system parses all parameters correctly
**And** stores the override flag for use later in the pipeline

**Given** invalid or missing parameters
**When** I type `/pe` (without prompt)
**Then** the system shows helpful error message
**And** suggests correct syntax: /pe "your prompt here"

---

### Story 1.2: Display Real-Time Progress Messages

As a **developer waiting for enhancement results**,
I want **to see progress messages during processing** (🔍 Analyzing... 🚀 Enhancing...),
So that **I know the system is working and understand what stage it's in**.

**Acceptance Criteria:**

**Given** the /pe command is executing
**When** analyzing project (Phase 1)
**Then** display "🔍 Analyzing project..." message
**And** show progress percentage or elapsed time

**Given** analysis is complete
**When** starting enhancement generation (Phase 2)
**Then** clear previous message
**And** display "🚀 Enhancing prompt..." message

**Given** enhancement is complete
**When** starting result formatting (Phase 3)
**Then** display "✓ Complete!" with final results

**Given** any processing stage takes >3 seconds
**When** still processing
**Then** update progress message periodically (every 2-3 seconds)
**And** show estimated time remaining if possible

**Given** an error occurs during processing
**When** processing fails at any stage
**Then** display phase-specific error message
**And** provide recovery guidance

---

### Story 1.3: Format and Display Results in Display-Only Mode

As a **developer reviewing enhancement results**,
I want **to see original prompt, enhanced prompt, and implementation steps in Display-Only mode**,
So that **I can review before deciding to use the enhancement**.

**Acceptance Criteria:**

**Given** enhancement is complete
**When** displaying results
**Then** show three distinct sections:
  1. Original Prompt (with quotation)
  2. Enhanced Prompt (with clear visual separation)
  3. Implementation Steps (numbered, actionable)

**Given** Display-Only mode is active
**When** results are displayed
**Then** results are NOT auto-executed
**And** user must explicitly review and approve
**And** each section is clearly marked with emoji (📝, ✨, 🔧)

**Given** the output is for Claude Code terminal
**When** formatting results
**Then** use plain text with clear ASCII separators
**And** use emoji for visual clarity
**And** structure for readability by screen readers

**Given** results include long text
**When** displaying enhancement
**Then** wrap text appropriately for 80-character terminal width
**And** maintain readability without color codes

---

### Story 1.4: Implement 5-15 Second Performance Target

As a **developer in creative flow**,
I want **the `/pe` command to complete in 5-15 seconds maximum**,
So that **I can iterate rapidly without losing momentum**.

**Acceptance Criteria:**

**Given** a typical project
**When** executing /pe command
**Then** 95% of requests complete within 5-15 seconds
**And** performance is measured in actual Claude Code environment
**And** target is achieved with current parallelization strategy

**Given** caching is available
**When** executing /pe on previously analyzed project
**Then** response time is <2 seconds (from cache)
**And** cache fingerprint is validated before using cached data

**Given** multiple analysis phases (1-5s, API call 30s, formatting 3s)
**When** any phase approaches timeout
**Then** system gracefully handles and moves to next phase
**And** hard timeout of 60 seconds (Claude Code limit) is never exceeded

**Given** a slow project (large codebase, slow Git)
**When** analyzing
**Then** system uses intelligent sampling to meet 5-15s target
**And** degrades gracefully if timeout imminent

---

**✓ Epic 1 Complete: 4 stories, all 10 FRs covered**

---

## Epic 2: Automatic Project & Standards Analysis

System automatically detects project type, structure, Git history, and coding conventions without user intervention, creating a "just understands my project" experience.

### Story 2.1: Detect Project Type from Filesystem Markers

As a **system analyzing a project**,
I want **to automatically detect the project programming language and type**,
So that **I can apply language-specific analysis and standards detection**.

**Acceptance Criteria:**

**Given** a Python project with `requirements.txt` or `pyproject.toml`
**When** analyzing the project root
**Then** system identifies it as Python project
**And** records Python version from metadata if available

**Given** a Node.js project with `package.json`
**When** analyzing the project
**Then** system identifies it as JavaScript/Node.js project
**And** records Node version from package.json

**Given** a Go project with `go.mod`
**When** analyzing the project
**Then** system identifies it as Go project

**Given** a Rust project with `Cargo.toml`
**When** analyzing the project
**Then** system identifies it as Rust project

**Given** a Java project with `pom.xml` or `build.gradle`
**When** analyzing the project
**Then** system identifies it as Java project

**Given** a project with mixed indicators
**When** multiple language markers exist
**Then** system identifies primary language based on file count/size
**And** notes secondary languages detected

---

### Story 2.2: Identify Project Indicator Files

As a **system understanding project structure**,
I want **to identify key project configuration and metadata files**,
So that **I can extract meaningful context about the project**.

**Acceptance Criteria:**

**Given** a project directory
**When** scanning for indicator files
**Then** system identifies all relevant files for the language:
  - `package.json` (Node.js)
  - `requirements.txt`, `pyproject.toml` (Python)
  - `go.mod` (Go)
  - `Cargo.toml` (Rust)
  - `pom.xml`, `build.gradle` (Java)
  - `.csproj` (C#)

**Given** indicator files found
**When** reading metadata
**Then** system extracts:
  - Project name and version
  - Dependencies and their versions
  - Package managers used
  - Build configuration

**Given** multiple lock files exist (`package-lock.json`, `Pipfile.lock`)
**When** analyzing
**Then** system notes presence of lock files
**And** records consistency of dependency management

**Given** configuration files missing
**When** indicator files not found
**Then** system gracefully handles and notes "standard project configuration not found"
**And** continues with other analysis methods

---

### Story 2.3: Extract Git History and Project Context

As a **system understanding development patterns**,
I want **to analyze Git history for commits, branches, and activity patterns**,
So that **I can understand the project's development methodology**.

**Acceptance Criteria:**

**Given** a Git repository
**When** analyzing Git history
**Then** system reads:
  - Total commit count
  - Current branch name
  - Recent commit messages (last 10)
  - Branch structure

**Given** Git history is available
**When** analyzing commits
**Then** system identifies:
  - Primary contributors
  - Commit frequency (commits per week)
  - Active development period
  - Repository age

**Given** non-Git project or Git access restricted
**When** attempting Git analysis
**Then** system gracefully skips Git analysis
**And** continues with other detection methods
**And** logs that Git context unavailable

**Given** large repository with many commits
**When** reading history
**Then** system uses efficient log reading (not full history)
**And** reads last N commits efficiently (N = configurable, default 100)

---

### Story 2.4: Generate Project Fingerprint for Caching

As a **system ensuring consistent detection across runs**,
I want **to generate a unique fingerprint of the project**,
So that **I can validate cache and ensure same project always gets same analysis**.

**Acceptance Criteria:**

**Given** a project is analyzed
**When** generating fingerprint
**Then** system computes hash of:
  - Package/configuration files (package.json, requirements.txt, etc.)
  - Git log count (or 0 if non-Git)
  - Language/framework metadata

**Given** same project analyzed multiple times
**When** fingerprints compared
**Then** fingerprint is identical (deterministic)
**And** system can confidently use cached results

**Given** project files modified
**When** project is re-analyzed
**Then** fingerprint changes
**And** system invalidates cache
**And** forces re-analysis

**Given** cache validation check
**When** checking if cache valid
**Then** compare fingerprints
**And** check TTL (24-hour default)
**And** use cache only if both match

---

### Story 2.5: Detect Naming Conventions

As a **system understanding code style**,
I want **to analyze source files and detect naming convention patterns**,
So that **I can identify how developers name functions, variables, classes**.

**Acceptance Criteria:**

**Given** a project with source files
**When** sampling 50-100 representative files
**Then** system analyzes naming patterns in:
  - Function/method names
  - Variable names
  - Class/type names
  - Module/file names

**Given** source file analysis
**When** detecting conventions
**Then** system identifies:
  - snake_case usage (validate_email, user_service)
  - camelCase usage (validateEmail, userService)
  - PascalCase usage (ValidateEmail, UserService)
  - kebab-case usage (validate-email, user-service)

**Given** mixed conventions detected
**When** analyzing
**Then** system categorizes by:
  - Dominant convention (>60% of cases)
  - Secondary convention (20-60%)
  - Rare convention (<20%)

**Given** special cases
**When** detecting conventions
**Then** system distinguishes:
  - Function naming vs. class naming (may differ)
  - Private vs. public naming (underscore prefix, etc.)
  - Constants (UPPER_SNAKE_CASE)

---

### Story 2.6: Detect Test Framework

As a **system understanding project testing**,
I want **to identify which testing framework the project uses**,
So that **I can generate test code that matches project conventions**.

**Acceptance Criteria:**

**Given** a Python project
**When** detecting test framework
**Then** system identifies:
  - pytest (from `pytest.ini`, `conftest.py`, test imports)
  - unittest (from imports, test structure)
  - Other frameworks (nose, hypothesis, etc.)

**Given** a JavaScript project
**When** detecting test framework
**Then** system identifies:
  - Jest (from package.json, jest.config.js)
  - Mocha (from mocha config, test file patterns)
  - Other frameworks (Vitest, Jasmine, etc.)

**Given** a Java project
**When** detecting test framework
**Then** system identifies:
  - JUnit (4 or 5, from dependencies)
  - TestNG (from configuration)
  - Others (Spock, Cucumber, etc.)

**Given** test files detected
**When** analyzing
**Then** system notes:
  - Test directory location (test/, tests/, __tests__, spec/)
  - Test file naming pattern (test_*.py, *.test.js, *Test.java)
  - Test configuration files (pytest.ini, jest.config.js, etc.)

**Given** no test framework detected
**When** analyzing
**Then** system gracefully records "no standard test framework detected"
**And** flags as opportunity for improvement

---

### Story 2.7: Detect Documentation Style

As a **system understanding code documentation**,
I want **to identify the documentation/docstring style used**,
So that **I can generate documentation that matches project conventions**.

**Acceptance Criteria:**

**Given** a Python project
**When** analyzing docstrings
**Then** system identifies:
  - Google docstring style (google-style docstrings)
  - NumPy style (numpy-style docstrings)
  - Sphinx style (sphinx documentation)
  - PEP 257 style

**Given** a JavaScript project
**When** analyzing comments
**Then** system identifies:
  - JSDoc style (standard)
  - TypeDoc style (for TypeScript)
  - Custom comment styles

**Given** a Java project
**When** analyzing comments
**Then** system identifies:
  - JavaDoc style (standard)
  - Custom patterns

**Given** documentation style detected
**When** recording
**Then** system notes:
  - Presence of type hints (Python) or type annotations
  - Parameter documentation pattern
  - Return value documentation pattern
  - Exception documentation

**Given** inconsistent documentation
**When** analyzing
**Then** system identifies dominant style
**And** flags inconsistencies

---

### Story 2.8: Detect Code Organization Patterns

As a **system understanding project architecture**,
I want **to identify how the project organizes code**,
So that **I can generate suggestions aligned with project structure**.

**Acceptance Criteria:**

**Given** a project directory structure
**When** analyzing organization
**Then** system identifies patterns:
  - By-feature organization (features/auth/, features/payment/)
  - By-layer organization (models/, services/, controllers/)
  - By-type organization (utils/, helpers/, handlers/)
  - Domain-driven design (domains/users/, domains/orders/)

**Given** directory structure analyzed
**When** detecting pattern
**Then** system notes:
  - Primary organization principle
  - Consistency of pattern across project
  - Exceptions or special cases
  - Whether monolithic or modular

**Given** code organization detected
**When** recording
**Then** system identifies:
  - Location of main application code
  - Location of tests
  - Location of configuration
  - Location of utilities/shared code
  - Whether single or multiple entry points

---

### Story 2.9: Generate Confidence Scores for Standards Detection

As a **system communicating detection accuracy**,
I want **to calculate confidence scores for each detected standard**,
So that **users can see how confident the system is**.

**Acceptance Criteria:**

**Given** all standards detected (naming, testing, documentation, organization)
**When** calculating confidence
**Then** for each standard, system generates:
  - Confidence score (0-100%)
  - Sample size analyzed (e.g., "89 files analyzed")
  - Evidence (concrete examples from code)
  - Exceptions noted (files that don't follow pattern)

**Given** high confidence (>85%)
**When** scoring
**Then** system marks as "High confidence"
**And** provides clear examples

**Given** medium confidence (60-85%)
**When** scoring
**Then** system marks as "Medium confidence"
**And** notes any inconsistencies

**Given** low confidence (<60%)
**When** scoring
**Then** system marks as "Low confidence"
**And** recommends user verification
**And** triggers warning during enhancement generation

**Given** confidence calculation
**When** computing score
**Then** system considers:
  - Number of files analyzed (larger sample = higher confidence)
  - Consistency of pattern (100% consistent = higher confidence)
  - Distinction between standards (auto-generated vs. user code)

---

### Story 2.10: Handle Claude Code Sandbox File Restrictions

As a **system operating in Claude Code environment**,
I want **to gracefully handle file access restrictions**,
So that **analysis continues despite permission limitations**.

**Acceptance Criteria:**

**Given** a file is inaccessible due to permissions
**When** analyzing project
**Then** system:
  - Catches permission error gracefully
  - Skips that file
  - Continues with other files
  - Notes file in access denied log

**Given** critical project files are inaccessible
**When** continuing analysis
**Then** system adapts:
  - Uses accessible files for detection
  - May reduce sample size
  - Adjusts confidence score accordingly
  - Provides warning about incomplete analysis

**Given** entire directories inaccessible
**When** sampling files
**Then** system:
  - Skips those directories
  - Samples from accessible directories
  - Maintains statistically valid sample
  - Notes limitation

**Given** analysis completes with restrictions
**When** finalizing detection
**Then** system includes in output:
  - Number of files inaccessible
  - Quality assessment (complete, partial, limited)
  - Recommended actions (try with broader permissions if possible)

**Given** Claude Code sandbox environment
**When** operating
**Then** system respects:
  - File access boundaries
  - Environment variable availability
  - API availability constraints

---

**✓ Epic 2 Complete: 10 stories, all 18 FRs covered**

---

## Epic 3: Project-Aware Prompt Enhancement

LLM uses detected project context to generate enhancements that respect project conventions, architecture patterns, and include implementation steps specific to the project.

### Story 3.1: Build Enhancement Prompt - Collect Project Context

As a **enhancement generation system**,
I want **to collect and organize all relevant project context information**,
So that **the LLM can use this information to generate project-aware enhancements**.

**Acceptance Criteria:**

**Given** project analysis is complete (type, structure, standards detected)
**When** building LLM prompt
**Then** system collects following context:
  - Project name, language, framework version
  - Detected coding standards (naming, testing, documentation)
  - Project organization pattern
  - Git history summary (commit frequency, development phase)
  - Key dependencies and libraries

**Given** user provided text prompt
**When** building enhancement prompt
**Then** system creates structured message containing:
  1. Original user prompt (unchanged)
  2. Project context (metadata)
  3. Detected coding standards
  4. Any user-defined rules or overrides

**Given** low-confidence standards detected (<60%)
**When** included in context
**Then** system marks these as low-confidence
**And** includes confidence scores
**And** includes sample evidence

**Given** sensitive information (like API keys)
**When** building prompt
**Then** system excludes any sensitive information
**And** never includes keys in any prompt
**And** only includes non-sensitive metadata

---

### Story 3.2: Call LLM to Generate Project-Aware Enhancement

As a **prompt enhancement system**,
I want **to send project context and detected standards to LLM for enhancement**,
So that **enhancements follow project conventions and include implementation guidance**.

**Acceptance Criteria:**

**Given** project context is prepared
**When** calling LLM API
**Then** system:
  - Uses OpenAI API (primary) or DeepSeek (fallback)
  - Sends single API call (not batched separately)
  - Includes project context in system prompt
  - Includes original prompt in user message

**Given** LLM API call in progress
**When** processing response
**Then** system:
  - Waits for full response (not streaming)
  - Times out after 5 seconds to start returning error (maximum 30 seconds)
  - Catches API errors and returns friendly error message

**Given** LLM returns enhanced prompt
**When** validating response
**Then** system checks:
  - Response is not empty
  - Contains actionable guidance
  - Preserves original user intent
  - Reasonable length (not exceeding 2000 characters)

**Given** API call fails or times out
**When** handling failure
**Then** system:
  - Retries once if possible
  - Checks for cached standards
  - Degrades to generic enhancement (no project awareness)
  - Displays quality warning

**Given** project has custom enhancement template
**When** calling LLM
**Then** system includes template guidance in prompt
**And** instructs LLM to follow template format

---

### Story 3.3: Generate Project-Specific Implementation Steps and Verification Criteria

As a **enhancement prompt system**,
I want **to ensure enhancement includes project-specific implementation steps and verification standards**,
So that **developers get immediately actionable guidance**.

**Acceptance Criteria:**

**Given** LLM generates enhanced prompt
**When** post-processing enhancement result
**Then** system validates inclusion of:
  - **Implementation Steps**: Step-by-step, project-specific steps
  - **Verification Criteria**: How to know implementation succeeded
  - **Testing Guidance**: Suggestions using detected test framework
  - **Standards Application**: Concrete examples following project conventions

**Given** detected coding standards (e.g., snake_case naming)
**When** generating code examples
**Then** system:
  - Names functions/variables using detected conventions
  - Uses detected code organization patterns
  - Writes tests using detected test framework
  - Writes comments using detected documentation style

**Given** project uses specific architecture pattern (e.g., by-feature)
**When** suggesting code locations
**Then** system:
  - Recommends files in correct directories
  - Suggests following existing patterns
  - Provides paths relative to project structure

**Given** multiple possible implementation approaches
**When** generating steps
**Then** system:
  - Recommends approach most aligned with project
  - Explains why this approach chosen
  - Includes alternative approaches as comments

**Given** low-confidence detected standards
**When** generating guidance
**Then** system:
  - Includes optional override instructions
  - Suggests user verify detection
  - Allows easy customization of standards

---

**✓ Epic 3 Complete: 3 stories, all 6 FRs covered**

---

## Epic 4: Standards Visibility & User Control

System displays detected standards with confidence scores and evidence, allowing users to customize at three levels (global project, per-request, template-based).

### Story 4.1: Display Detected Standards with Confidence Scores

As a **enhancement system**,
I want **to display all detected coding standards with confidence scores and evidence**,
So that **users see how the system understands their project**.

**Acceptance Criteria:**

**Given** project analysis and standards detection complete
**When** displaying results
**Then** system displays all 5 standards:
  - Naming convention (e.g., snake_case 90% confidence)
  - Test framework (e.g., pytest 95% confidence)
  - Documentation style (e.g., Google docstrings 85% confidence)
  - Code organization (e.g., by-feature 80% confidence)
  - Module naming (e.g., service_*.py 88% confidence)

**Given** standards detected
**When** displaying information
**Then** each standard includes:
  - Standard name and detected value
  - Confidence score (0-100%)
  - Sample size ("analyzed in 89 files")
  - Concrete evidence examples
  - Any exceptions noted

**Given** high-confidence standards (>85%)
**When** displaying
**Then** marked as "High confidence"
**And** clear examples provided

**Given** low-confidence standards (<60%)
**When** displaying
**Then** marked as "Low confidence"
**And** suggests user verification
**And** provides override method

**Given** mixed conventions detected
**When** displaying results
**Then** system shows:
  - Dominant convention (>60%)
  - Secondary convention (20-60%)
  - Exceptions explained

---

### Story 4.2: Project-Level Standards Configuration (`.pe.yaml`)

As a **developer**,
I want **to set coding standards once in a project configuration file**,
So that **all subsequent `/pe` commands use these standards without reconfiguration**.

**Acceptance Criteria:**

**Given** user creates `.claude/pe-config.yaml` file
**When** `/pe` command executes
**Then** system:
  - Reads project-level configuration file
  - Overrides auto-detected standards
  - Applies these standards to all enhancements for this project
  - Shows "Using project configuration standards" message

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

**Given** configuration file contains invalid values
**When** parsing configuration
**Then** system:
  - Shows friendly error message
  - Suggests correct values
  - Falls back to auto-detection

**Given** project-level configuration exists
**When** conflicts with auto-detection
**Then** system prioritizes project configuration
**And** logs override in debug log

**Given** configuration file updated
**When** change detected
**Then** system:
  - Rereads configuration
  - Applies new standards
  - No restart needed

---

### Story 4.3: Per-Request Override (`--override` flag)

As a **developer**,
I want **to temporarily override specific standards in a single `/pe` command**,
So that **I can experiment with different conventions without modifying project configuration**.

**Acceptance Criteria:**

**Given** user executes `/pe` command
**When** includes `--override` flag
**Then** system parses override parameters:
  - `--override naming=camelCase`
  - `--override test_framework=jest`
  - `--override documentation=jsdoc`
  - Supports multiple overrides: `--override naming=camelCase --override test_framework=jest`

**Given** override flag provided
**When** generating enhancement
**Then** system:
  - Uses override value instead of detected/configured value
  - Shows "Using overridden standards" message
  - Applies override only to this request
  - Does not modify project configuration

**Given** invalid override value
**When** parsing parameters
**Then** system:
  - Shows list of valid values
  - Example: `--override naming=[snake_case|camelCase|PascalCase|kebab-case]`
  - Falls back to detected/configured value

**Given** multiple overrides same standard
**When** conflicting values provided
**Then** system uses last value
**And** shows warning about override

**Given** user wants to experiment with standards
**When** using override
**Then** system:
  - Does not save override to project configuration
  - Applies only to current request
  - Provides clear feedback about what's in use

---

### Story 4.4: Template System and Save User Overrides

As a **developer**,
I want **to use predefined standard templates or save my custom standard configurations**,
So that **I can quickly switch standards between projects or reuse common configurations**.

**Acceptance Criteria:**

**Given** user wants to use template
**When** executes `/pe --template fastapi "my prompt"`
**Then** system:
  - Loads predefined FastAPI template standards
  - Applies these standards to enhancement
  - Shows "Using fastapi template" message

**Given** predefined templates exist
**When** listing available templates
**Then** system includes:
  - `fastapi` - FastAPI web framework standards
  - `django` - Django web framework standards
  - `flask` - Flask web framework standards
  - `react` - React application standards
  - `generic` - Generic defaults

**Given** user saves custom standards
**When** creating custom template
**Then** system:
  - Saves to `~/.prompt-enhancement/templates/my-template.yaml`
  - Allows user to reference as `/pe --template my-template "prompt"`
  - Provides template edit command

**Given** user applies overrides in multiple requests
**When** suggesting to save as template
**Then** system:
  - Suggests saving override as template
  - Provides `/pe-save-template my-name` command
  - Asks for template name and description

**Given** template and project configuration conflict
**When** executing `/pe --template X` (project has custom config)
**Then** system:
  - Prioritizes template
  - Shows message: "Using my-template, overriding project configuration"
  - Still allows `--override` for further customization

---

**✓ Epic 4 Complete: 4 stories, all 6 FRs covered**

---

## Epic 5: Robust Error Handling & Graceful Degradation

System gracefully handles failures with 5-category error classification, user-friendly messages, and 3-level degradation strategy to maintain value even when constraints encountered.

### Story 5.1: Error Classification and User-Friendly Messages

As a **error handling system**,
I want **to classify errors into 5 categories and provide specific user guidance for each**,
So that **developers know what went wrong and how to fix it**.

**Acceptance Criteria:**

**Given** an error occurs during system operation
**When** error is caught
**Then** system classifies into one of 5 categories:
  1. **API_KEY_MISSING** - Both OPENAI_API_KEY and DEEPSEEK_API_KEY not found
  2. **PROJECT_NOT_DETECTED** - Unable to identify project type
  3. **DETECTION_FAILED** - Standards detection confidence <60%
  4. **API_TIMEOUT** - LLM API call exceeds 20 seconds
  5. **PERMISSION_DENIED** - Cannot access some project files

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

**Given** DETECTION_FAILED error occurs
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

**Given** error message displayed to user
**When** choosing language
**Then** system shows:
  - Clear symptom (❌ symbol)
  - Simple English or user language
  - Specific resolution steps
  - No technical jargon or internal codes

---

### Story 5.2: Graceful Degradation Mechanism (3 Levels)

As a **enhancement system**,
I want **to automatically degrade to lower functionality level rather than completely failing**,
So that **users still get some value even if not full functionality**.

**Acceptance Criteria:**

**Given** full enhancement fails but degradation possible
**When** evaluating degradation strategy
**Then** system implements 3 degradation levels:

**Level 1 - Full Enhancement (Ideal)**
- ✓ Automatic project detection complete
- ✓ Coding standards fully detected
- ✓ LLM enhancement includes project-specific implementation steps
- ✓ High quality output

**Level 2 - Enhancement Without Standards**
- ✓ Project detection successful
- ✓ Coding standards detection failed/timeout
- ✓ LLM enhancement lacks standards-specific guidance
- ⚠️ Reduced quality but has basic value

**Level 3 - Generic Enhancement**
- ✓ Basic prompt enhancement
- ✗ No project context
- ✗ No coding standards
- ⚠️ Minimum quality but still some value

**Given** project detection fails
**When** evaluating possible continuation
**Then** system:
  - Automatically degrades to Level 2 or 3
  - Displays quality warning
  - Shows degradation reason

**Given** standards detection confidence low (<60%)
**When** continuing enhancement
**Then** system:
  - Selects Level 2 degradation
  - Shows "Low confidence in standards detection" warning
  - Continues with standards-free enhancement

**Given** LLM API timeout (>20 seconds)
**When** handling timeout
**Then** system:
  - Checks for cached standards
  - Uses Level 2 if cache available
  - Degrades to Level 3 if no cache
  - Shows "API timeout, using cached standards" message

**Given** permission denied analyzing files
**When** continuing analysis
**Then** system:
  - Uses accessible files
  - Adjusts confidence scores
  - May select Level 2 degradation
  - Shows "File access restricted" warning

---

### Story 5.3: User Confirmation of Degradation Decision

As a **user**,
I want **to confirm before system degrades to lower quality level**,
So that **I can decide whether to continue or stop**.

**Acceptance Criteria:**

**Given** system detects need for degradation
**When** evaluating degradation possibility
**Then** system does not auto-degrade, instead:
  1. Shows degradation warning
  2. Explains why degradation needed
  3. Shows expected quality level
  4. Asks user whether to continue

**Given** degradation confirmation prompt displayed
**When** waiting for user input
**Then** system shows:
  ```
  ⚠️ Project Detection Failed - Quality Will Degrade

  System could not auto-detect project type.
  Suggested degradation level: Level 3 (Generic Enhancement)

  Would you like to:
  [Y] Continue (Accept degraded quality)
  [N] Stop (Cancel enhancement)
  [T] Troubleshoot (View diagnostic info)
  ```

**Given** user selects [Y]
**When** continuing
**Then** system:
  - Shows "Continuing in degraded mode"
  - Applies corresponding degradation level
  - Marks output as degraded quality

**Given** user selects [N]
**When** stopping
**Then** system:
  - Cancels enhancement operation
  - Shows "Enhancement cancelled"
  - Performs no processing

**Given** user selects [T]
**When** troubleshooting
**Then** system shows:
  - Diagnostic information (what detection attempted)
  - Detailed error reasons
  - Potential fix suggestions

---

### Story 5.4: Error Recovery and Logging

As a **system maintainer**,
I want **to log all errors for debugging and provide recovery options to users**,
So that **issues can be diagnosed and resolved**.

**Acceptance Criteria:**

**Given** any error occurs
**When** handling error
**Then** system logs:
  - Timestamp (ISO 8601 format)
  - Error category
  - Error message
  - Stack trace (DEBUG mode only)
  - Project fingerprint (for project identification)

**Given** log level configuration
**When** logging errors
**Then** system supports levels:
  - **DEBUG**: All detailed information (development use)
  - **INFO**: Key events (standard)
  - **WARNING**: Warnings and errors only
  - **ERROR**: Errors only

**Given** log storage location
**When** writing logs
**Then** system:
  - Writes to `~/.prompt-enhancement/logs/pe.log`
  - Rotates logs (daily or 10MB)
  - Retains last 7 days of logs
  - Allows user to configure log level

**Given** error occurs and displayed to user
**When** providing recovery suggestions
**Then** system shows:
  ```
  ❌ An Error Occurred

  Diagnostic information saved to:
  ~/.prompt-enhancement/logs/pe.log

  Suggested steps:
  1. Check logs for detailed information
  2. [Error-specific recovery steps]
  3. Retry the operation
  4. If issue persists, report the issue
  ```

**Given** user wants to view logs
**When** using `/pe-logs` command
**Then** system:
  - Shows recent log entries
  - Allows filtering by level
  - Allows searching by keyword
  - Shows log file location

**Given** sensitive information potentially in logs
**When** logging information
**Then** system:
  - Never logs API keys
  - Never logs user prompts
  - Never logs enhancement results
  - Only logs metadata and error information

---

**✓ Epic 5 Complete: 4 stories, all 7 FRs covered**

---

## Epic 6: User Onboarding & Help System

New users can quickly learn and configure the system through 3-step quick guide, setup command, comprehensive help, and auto-generated template suggestions.

### Story 6.1: First-Time User 3-Step Quick Guide

As a **first-time user**,
I want **to see a 3-step quick guide when executing `/pe` for the first time**,
So that **I can immediately understand how the system works and what it does**.

**Acceptance Criteria:**

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

**Given** user completes one of the 3 steps
**When** executes `/pe` again
**Then** system:
  - Does not show quick guide again
  - Processes command directly
  - Remembers user has seen guide

**Given** user wants to see guide again
**When** executes `/pe-quickstart`
**Then** system displays full 3-step quick guide again

**Given** first-time setup complete
**When** system initializes configuration
**Then** system stores flag indicating user completed onboarding
  - Saved in `~/.prompt-enhancement/config.yaml`
  - Marked as `first_time_setup_complete: true`

---

### Story 6.2: `/pe-setup` Command for Initial Configuration

As a **new developer**,
I want **to run `/pe-setup` for interactive configuration of my API key and project preferences**,
So that **I can quickly get the system running without manually editing config files**.

**Acceptance Criteria:**

**Given** user runs `/pe-setup` command
**When** initializing setup flow
**Then** system displays interactive questionnaire:

```
🔧 Prompt Enhancement Setup Wizard

Step 1: API Key Configuration
  Please enter your OpenAI API key:
  [sk-...]

  Successfully configured! ✓

Step 2: Project Type (Optional)
  Detected project type: Python
  Is this correct? [Y/n]

Step 3: Standards Preferences (Optional)
  Naming convention: [snake_case / camelCase / other]
  Test framework: [pytest / unittest / other]

✅ Setup Complete!
You can now run: /pe "your prompt"
```

**Given** user enters valid API key
**When** validating key
**Then** system:
  - Tests key with OpenAI API
  - Shows "✓ API key valid"
  - Saves to `~/.prompt-enhancement/config.yaml`

**Given** user enters invalid API key
**When** validation fails
**Then** system:
  - Shows "❌ API key invalid"
  - Allows re-entry
  - Provides help link for getting key

**Given** setup complete
**When** user confirms
**Then** system:
  - Saves all settings to config file
  - Shows "✅ Setup Complete"
  - Suggests next step: `/pe-help`

**Given** user wants to skip a step
**When** presses [Enter] or types "skip"
**Then** system:
  - Skips that step
  - Uses defaults or auto-detection
  - Continues to next step

---

### Story 6.3: `/pe-help` Command and Auto Template Suggestions

As a **user learning the system**,
I want **to run `/pe-help` to see complete documentation, examples, and available templates**,
So that **I understand all features and advanced options**.

**Acceptance Criteria:**

**Given** user runs `/pe-help` command
**When** requesting help
**Then** system displays comprehensive help guide:

```
📚 Prompt Enhancement Complete Help

🚀 Basic Usage:
  /pe "Your prompt"

  Example:
  /pe "How to implement user authentication?"

⚙️ Advanced Options:

  Configure Project Standards:
  /pe --override naming=camelCase "prompt"

  Use Templates:
  /pe --template fastapi "prompt"

  View Detected Standards:
  /pe --show-standards

📋 Available Templates:
  fastapi    - FastAPI Web Framework
  django     - Django Web Framework
  flask      - Flask Web Framework
  react      - React Application
  generic    - Generic Defaults

🔧 Commands:
  /pe-setup      - Initialize configuration
  /pe-help       - Show this help
  /pe-logs       - View diagnostic logs
  /pe-clear-cache - Clear cached standards

📖 Full Documentation:
  Run: /pe --help-full
  Or see: docs/README.md

💡 FAQ:
  Q: How do I change coding standards?
  A: Run /pe-setup or use --override flag

  Q: How do I save custom templates?
  A: After configuring standards, run /pe-save-template my-name

Need more help? Check full documentation or submit an issue.
```

**Given** first run on detected project
**When** system analyzes project
**Then** system automatically suggests relevant template:

```
🎯 Recommended Template (based on your project):

Detected FastAPI project
Recommended template: fastapi

You can run:
  /pe --template fastapi "your prompt"

Or create project configuration:
  /pe-setup

Continue? [Y/n]
```

**Given** user selects suggested template
**When** accepting suggestion
**Then** system:
  - Remembers preference
  - Auto-uses template for same project going forward
  - Shows "Using fastapi template" message

**Given** user runs `/pe --help-full`
**When** requesting full help
**Then** system displays:
  - Detailed documentation for all commands
  - Complete examples
  - Configuration file formats
  - Troubleshooting guide

**Given** user viewing help
**When** looking for specific topic
**Then** system allows:
  - `/pe-help standards` - Coding standards details
  - `/pe-help templates` - Template system details
  - `/pe-help config` - Configuration file details
  - `/pe-help examples` - Usage examples

---

**✓ Epic 6 Complete: 3 stories, all 5 FRs covered**

---

## Summary: All Epics Complete

✅ **Epic 1: Fast & Responsive `/pe` Command** - 4 stories, 10 FRs
✅ **Epic 2: Automatic Project & Standards Analysis** - 10 stories, 18 FRs
✅ **Epic 3: Project-Aware Prompt Enhancement** - 3 stories, 6 FRs
✅ **Epic 4: Standards Visibility & User Control** - 4 stories, 6 FRs
✅ **Epic 5: Robust Error Handling & Graceful Degradation** - 4 stories, 7 FRs
✅ **Epic 6: User Onboarding & Help System** - 3 stories, 5 FRs

**Total: 28 stories covering all 54 FRs + 29 NFRs**
