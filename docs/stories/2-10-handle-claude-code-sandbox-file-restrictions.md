# Story 2.10: Handle Claude Code Sandbox File Restrictions

**Story ID**: 2.10
**Epic**: Epic 2 - Automatic Project & Standards Analysis
**Status**: drafted
**Created**: 2025-12-18

---

## Story

As a **system operating in Claude Code environment**,
I want **to gracefully handle file access restrictions and permission limitations**,
So that **analysis continues despite sandbox constraints and maintains statistical validity**.

---

## Acceptance Criteria

### AC1: Graceful Permission Error Handling
**Given** a file or directory is inaccessible due to permissions
**When** analyzing project
**Then** system:
- Catches PermissionError, FileNotFoundError, OSError exceptions
- Logs inaccessible path to access_denied list
- Skips that file/directory
- Continues with other files
- Does not crash or interrupt analysis
**And** preservation of analysis integrity

### AC2: File Access Adaptation for Standards Detection
**Given** critical project files are inaccessible
**When** continuing standards detection
**Then** system adapts by:
- Using accessible files for detection
- Maintaining statistically valid sample size (min 20 files)
- Adjusting confidence scores based on sample completeness
- Providing warning about incomplete analysis
- Documenting which files were inaccessible
**And** analysis completes with adjusted metrics

### AC3: Directory Traversal Resilience
**Given** entire directories inaccessible (node_modules, .git, etc.)
**When** sampling files for analysis
**Then** system:
- Catches access errors during traversal
- Skips those directories silently
- Samples from accessible directories
- Maintains alphabetical order for consistency
- Provides coverage summary (X files analyzed out of Y in scope)
**And** skips don't impact detection validity

### AC4: Access Restriction Reporting
**Given** analysis completes with file access restrictions
**When** generating detection results
**Then** system includes:
- Count of inaccessible files
- List of denied paths (for debugging)
- Quality assessment (complete, partial, limited)
- Confidence adjustment factor (if applicable)
- Recommendation (analysis is valid / suggest retry with broader permissions)
**And** output clearly indicates analysis scope

### AC5: Confidence Score Adjustment
**Given** analysis incomplete due to access restrictions
**When** calculating confidence scores
**Then** system:
- Calculates access coverage percentage: (files_sampled / files_attempted) * 100
- If access_coverage >= 80%: No confidence adjustment
- If access_coverage 60-80%: Reduce confidence by 10%
- If access_coverage 40-60%: Reduce confidence by 20%
- If access_coverage < 40%: Reduce confidence by 30%, flag as "limited"
**And** original detection remains valid with adjusted confidence

### AC6: Integration with All Detection Modules
**Given** all detection modules (Stories 2.1-2.9) process files
**When** implementing file access handling
**Then** system:
- Provides unified file access API (try_read_file, safe_scan_directory)
- All detectors use common error handling patterns
- Detectors don't need individual permission logic
- Consistent error classification across modules
- Backward compatible with existing detectors
**And** each detector gracefully handles inaccessible files

### AC7: Claude Code Environment Compatibility
**Given** execution in Claude Code sandbox
**When** operating within file access boundaries
**Then** system:
- Respects Claude Code's file access restrictions
- Does not attempt to circumvent permissions
- Provides helpful guidance when access denied
- Identifies Claude Code environment detection
- Adapts sampling strategy based on environment
**And** operates reliably within sandbox constraints

### AC8: Detection Quality Maintenance
**Given** file access restrictions present
**When** finalizing detection results
**Then** system maintains quality by:
- Ensuring minimum sample size (at least 20 files analyzed)
- Maintaining statistical validity of pattern detection
- Flagging low-sample detections (< 30 files: confidence_quality = "limited")
- Providing actionable recommendations
- Documenting analysis scope clearly
**And** results remain trustworthy despite restrictions

---

## Technical Requirements (from Architecture)

### File Access Error Handling Architecture
- **Component**: File Access Handler (P0.1-P0.3 integration point)
- **Responsibility**: Provide unified file access API with graceful error handling
- **Pattern**: Try-catch wrapper with logging + result adaptation + confidence adjustment
- **Integration Point**: Used by all detection modules (Stories 2.1-2.9)
- **Performance Target**: No additional overhead (error handling is negligible)
- **Dependencies**: Python built-in OS/file operations, project detection results

### File Access API
```python
class FileAccessHandler:
    def try_read_file(
        self,
        file_path: str,
        encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Safely read file content, returning None if access denied.
        Logs denied access for reporting.
        """

    def safe_scan_directory(
        self,
        directory_path: str,
        pattern: str = "*",
        recursive: bool = True
    ) -> Tuple[List[str], List[str]]:
        """
        Scan directory safely, returning (accessible_files, denied_paths).
        Continues on access errors, logs denied paths.
        """

    def get_access_report(self) -> FileAccessReport:
        """
        Returns comprehensive access restriction report for output.
        Includes counts, paths, quality metrics, recommendations.
        """
```

### File Access Report Format
```python
@dataclass
class FileAccessReport:
    """Report on file access restrictions encountered"""
    total_files_attempted: int
    files_successfully_accessed: int
    files_access_denied: int
    access_coverage_percentage: float
    inaccessible_paths: List[str]
    quality_assessment: str  # "complete", "partial", "limited"
    confidence_adjustment: float  # 0.0-1.0 multiplier
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
```

### Error Handling Patterns
```python
# Pattern 1: Safe file reading
try:
    content = file_handler.try_read_file(file_path)
    if content is not None:
        # Process file
except Exception as e:
    # Already handled by handler, continue

# Pattern 2: Safe directory scanning
accessible_files, denied_paths = file_handler.safe_scan_directory(dir_path)
# Use accessible_files, log denied_paths

# Pattern 3: Confidence adjustment
base_confidence = calculate_confidence(samples)
access_report = file_handler.get_access_report()
adjusted_confidence = base_confidence * access_report.confidence_adjustment
```

### Confidence Adjustment Formula
```
access_coverage = (files_accessed / files_attempted) * 100

confidence_adjustment = {
    >= 80%: 1.0   (no adjustment),
    60-80%: 0.90  (10% reduction),
    40-60%: 0.80  (20% reduction),
    < 40%:  0.70  (30% reduction)
}

adjusted_confidence = original_confidence * confidence_adjustment
```

---

## Implementation Notes

### File Access Handler Implementation
- Centralized handler class manages all file access operations
- Try-catch blocks catch PermissionError, FileNotFoundError, IsADirectoryError, OSError
- Log all access denied paths for debugging and reporting
- Maintain counters for access statistics
- Return None or empty list rather than raising exceptions (graceful degradation)

### Integration with Detection Modules
- Import FileAccessHandler in each detector
- Replace direct file operations with handler calls
- Update detector constructors to accept handler instance
- Maintain backward compatibility (handler optional, defaults to None)
- No changes to public API or output format

### Access Report Calculation
- Track attempts vs successes during scanning
- Calculate coverage percentage at completion
- Map coverage to confidence adjustment multiplier
- Apply adjustment to all per-standard confidence scores
- Include report in detection output for transparency

### Edge Cases
- Handle symlink loops gracefully
- Handle very large files (read samples instead of full content)
- Handle binary files (skip with logging)
- Handle deeply nested directories (breadth-first instead of deep-first)
- Handle inaccessible parent directories (skip entire subtree)

### Performance Optimization
- Minimal overhead from exception handling
- Early termination on access denied (don't retry)
- Batch access denial logging (don't log every file)
- No retry logic (single attempt per file)

---

## Definition of Done

- [ ] Acceptance criteria documented (8 total)
- [ ] Test suite created with >80% coverage
- [ ] Implementation complete with all ACs passing
- [ ] Documentation/docstrings for code
- [ ] No new test failures (all existing tests pass)
- [ ] All detection modules updated to use file access handler
- [ ] Integrated into standards detection pipeline
- [ ] Commit message follows project standards
- [ ] Story file updated with completion notes

---

## Dev Agent Record

**Implementation Status**: In development

**Key Design Decisions**:
- Centralized FileAccessHandler for unified error handling
- Graceful degradation with confidence adjustment
- Try-catch at file/directory level (not per-operation)
- Access report for transparency and debugging
- No retry logic (respects permissions immediately)

**Testing Approach**:
- Test-Driven Development (RED → GREEN → REFACTOR)
- Unit tests for file access handler
- Integration tests with simulated permission errors
- Confidence adjustment validation
- All detection modules with file access handling
- Edge case handling (symlinks, binary files, deep nesting)

**Completion Notes**: Pending

---

## Epic 2 Completion Status

Story 2.10 is the final story for Epic 2. Upon completion:
- All 10 stories will be done
- 18 FRs will be covered (FR2.1-FR2.6, FR3.1-FR3.8, FR9.1-FR9.4)
- Project analysis pipeline will be complete
- Epic 2 will transition to "done" status
