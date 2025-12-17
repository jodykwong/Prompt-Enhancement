# Story 2.7: Detect Documentation Style

**Story ID**: 2.7
**Epic**: Epic 2 - Automatic Project & Standards Analysis
**Status**: drafted
**Created**: 2025-12-18

---

## Story

As a **system understanding documentation patterns**,
I want **to identify the documentation/docstring style used in the project**,
So that **I can generate documentation that matches project conventions**.

---

## Acceptance Criteria

### AC1: Python Documentation Style Detection
**Given** a Python project with docstrings
**When** analyzing documentation style
**Then** system identifies:
- Google-style docstrings (Args:, Returns:, Raises: sections)
- NumPy-style docstrings (Parameters, Returns, Raises sections with dashes)
- PEP 257 style (minimal, first line summary then blank line)
- Sphinx-style docstrings (`:param`, `:type`, `:return` directives)
- reStructuredText (reST) docstrings
**And** provides confidence score for each detected style
**And** handles mixed styles gracefully (reports all found)

### AC2: JavaScript/TypeScript Documentation Style Detection
**Given** a JavaScript/TypeScript project with comments
**When** analyzing documentation style
**Then** system identifies:
- JSDoc style (`/** ... */` with `@param`, `@returns`, `@throws` tags)
- TypeScript doc comments (similar structure with type information)
- Custom comment patterns used in project
**And** provides confidence score per style
**And** detects TypeScript-specific documentation patterns (generics, union types)

### AC3: Java Documentation Style Detection
**Given** a Java project with comments
**When** analyzing documentation style
**Then** system identifies:
- Javadoc style (`/** ... */` with `@param`, `@return`, `@throws` tags)
- Javadoc variants (HTML content within docstrings, code examples, `@see` references)
**And** detects javadoc usage frequency across classes, methods, fields
**And** returns confidence scores

### AC4: Go Documentation Style Detection
**Given** a Go project
**When** analyzing documentation style
**Then** system identifies:
- Go doc comments (comments directly preceding declarations)
- Comment format (single-line vs. multi-line)
- Doc comment conventions (starts with name of the thing being documented)
**And** detects usage patterns

### AC5: Documentation Presence Analysis
**Given** source files analyzed
**When** evaluating documentation
**Then** system detects:
- Overall documentation coverage % (% of functions/classes with docs)
- Documentation consistency across codebase
- Patterns in what is documented vs. undocumented
- Special documentation files (CONTRIBUTING.md, ARCHITECTURE.md, etc.)
**And** provides coverage metrics
**And** flags under-documented projects (< 25% coverage as threshold)

### AC6: Documentation Confidence Scoring
**Given** multiple detection methods available
**When** analyzing documentation styles
**Then** system:
- Assigns confidence based on evidence:
  * Direct docstring/comment patterns found (high: 0.9)
  * Frequency of pattern usage (affects confidence weighting)
  * Consistency across multiple files (boosts confidence)
  * Special markers (Google Args: sections, JSDoc @tags, etc.)
- Combines evidence sources
- Returns confidence score 0.0-1.0 for each detected style
- Flags uncertain cases (confidence < 0.5)

### AC7: Documentation Result Format
**Given** documentation analysis complete
**When** returning results
**Then** system provides:
- DocumentationStyleResult dataclass with:
  * Primary style (most likely, highest confidence)
  * Detected styles list (all found with confidence scores)
  * Documentation coverage percentage
  * Coverage metrics (documented functions, classes, etc.)
  * Special documentation files found (README, CONTRIBUTING, etc.)
  * Analysis notes (consistency, patterns, recommendations)
  * Timestamp and version for tracking

### AC8: Integration with Project Analysis
**Given** project analysis from Stories 2.1-2.6
**When** performing documentation style detection
**Then** system:
- Uses detected language (Story 2.1) to guide style detection
- Uses file list from Story 2.2 for analysis
- Works with naming conventions (Story 2.5) for pattern consistency
- Works with test framework (Story 2.6) for test documentation patterns
- Samples representative source files (similar to Story 2.5)
**And** returns results compatible with other detection modules
**And** completes within 2 seconds (performance budget)

---

## Technical Requirements (from Architecture)

### Documentation Detection Architecture
- **Component**: Documentation Style Detector (P0.2 phase, part of standards detection)
- **Responsibility**: Identify documentation/docstring style used by project
- **Pattern**: File scanning + pattern matching + regex analysis
- **Integration Point**: Standards detection pipeline after Stories 2.1-2.6
- **Performance Target**: Complete within 2 seconds
- **Dependencies**: Results from Story 2.1 (tech_stack), 2.2 (project_files)

### Detection Strategy
```
1. Get project language from Story 2.1
2. Get file list from Story 2.2
3. Sample representative source files (up to 100 files)
4. For each language:
   - Extract comments/docstrings using language-specific patterns
   - Classify docstring style by recognizing markers (Args:, @param, etc.)
   - Count occurrences of each style
   - Calculate documentation coverage
5. Compute confidence scores based on frequency and consistency
6. Identify special documentation files
7. Return consolidated result
```

### Style Detection Patterns

#### Python Documentation Styles

**Google Style Markers:**
```
Args:
    param_name (type): description
Returns:
    type: description
Raises:
    ExceptionType: description
```

**NumPy Style Markers:**
```
Parameters
----------
param_name : type
    description

Returns
-------
type
    description

Raises
------
ExceptionType
    description
```

**PEP 257 Style Markers:**
```
Short description.

Longer description if needed.
"""
```

**Sphinx/reST Style Markers:**
```
:param param_name: description
:type param_name: type
:return: description
:rtype: type
:raises ExceptionType: description
```

#### JavaScript/TypeScript Documentation Styles

**JSDoc Style Markers:**
```
/**
 * Description of function
 * @param {type} paramName - description
 * @returns {type} description
 * @throws {ErrorType} description
 */
```

**TypeScript Doc Comments:**
```
/**
 * Description
 * @param paramName - description (type inferred from signature)
 * @returns description
 */
```

#### Java Documentation Styles

**Javadoc Style Markers:**
```
/**
 * Description of class/method
 * @param paramName description
 * @return description
 * @throws ExceptionType description
 * @see OtherClass
 */
```

#### Go Documentation Styles

**Go Doc Comments:**
```
// Package mypackage provides ...
//
// More detail about package
package mypackage

// MyFunction does something
func MyFunction() {
```

---

## Implementation Notes

### File Sampling Strategy
- Sample up to 100 source files across language-specific patterns
- Exclude test files (test_*, _test.py, *.test.js, etc.)
- Exclude vendor/node_modules/third-party directories
- Include variety of file types (classes, functions, modules)

### Pattern Recognition
- Use regex patterns for style-specific markers (Args:, @param, etc.)
- Multi-line docstring detection (triple quotes for Python, /** */ for others)
- Handle mixed indentation and formatting variations
- Count consistent style usage across samples

### Performance Optimization
- 2-second time budget for complete analysis
- Early termination if confidence threshold reached (> 0.85)
- Efficient file I/O with streaming where possible
- Cache regex patterns to avoid recompilation

### Edge Cases
- Handle projects with no documentation
- Handle projects with mixed styles
- Handle encoded files (UTF-8, ASCII)
- Handle very large files (truncate for analysis)
- Handle projects with non-standard doc patterns

---

## Definition of Done

- [x] Acceptance criteria documented (8 total)
- [ ] Test suite created with >80% coverage
- [ ] Implementation complete with all ACs passing
- [ ] Documentation/docstrings for code
- [ ] No new test failures (all existing tests pass)
- [ ] Code review approved
- [ ] Integrated into standards detection pipeline
- [ ] Commit message follows project standards
- [ ] Story file updated with completion notes

---

## Dev Agent Record

**Implementation Status**: In development

**Key Design Decisions**:
- Multi-language support (Python, JavaScript, Java, Go)
- Confidence-based style detection with evidence weighting
- File sampling strategy to handle large projects
- Graceful handling of mixed or missing documentation styles

**Testing Approach**:
- Test-Driven Development (RED → GREEN → REFACTOR)
- Comprehensive test cases for each language and style
- Integration tests with other detection modules
- Performance validation within 2-second budget

**Completion Notes**: Pending
