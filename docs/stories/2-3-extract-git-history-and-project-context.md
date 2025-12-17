# Story 2.3: Extract Git History and Project Context

**Story ID**: 2.3
**Epic**: Epic 2 - Automatic Project & Standards Analysis
**Status**: review
**Created**: 2025-12-18
**Completed**: 2025-12-18

---

## Story

As a **system understanding development patterns**,
I want **to analyze Git history for commits, branches, and activity patterns**,
So that **I can understand the project's development methodology**.

---

## Acceptance Criteria

### AC1: Git Repository Detection and Basic Analysis
**Given** a project directory with Git repository
**When** analyzing Git history
**Then** system successfully reads:
- Total commit count
- Current branch name
- Repository initialization date
**And** continues even if Git is not available or access denied

### AC2: Recent Commit Analysis
**Given** Git history is available
**When** analyzing commits
**Then** system extracts:
- Last 10 recent commit messages
- Commit timestamps and dates
- Commit authors (name only, not email)
**And** parses meaningful message summaries

### AC3: Git Statistics and Development Patterns
**Given** commit history data available
**When** analyzing patterns
**Then** system identifies:
- Primary contributors (top 5 by commit count)
- Commit frequency (commits per week, average)
- Active development period (oldest to newest commit)
- Repository age (days since first commit)
- Branch structure (main branch name, count of branches)

### AC4: Efficient Large Repository Handling
**Given** large repository with many commits (1000+)
**When** reading history
**Then** system:
- Reads only last N commits (configurable, default=100)
- Does NOT read entire history (performance critical)
- Completes within 2-second budget even for large repos
- Uses `git log --max-count=N` for efficiency

### AC5: Graceful Degradation for Non-Git Projects
**Given** non-Git project OR Git access restricted OR .git directory missing
**When** attempting Git analysis
**Then** system:
- Gracefully skips Git analysis without crashing
- Returns empty/None GitHistoryResult
- Continues with other detection methods
- Logs "Git context not available" at debug level (non-fatal)
- Does NOT retry or throw exceptions

### AC6: Error Handling for Permission Issues
**Given** .git directory exists but restricted by permissions
**When** attempting to read Git history
**Then** system:
- Catches permission errors gracefully
- Logs error without exposing system details
- Returns None for Git context
- Treats same as non-Git project (AC5 behavior)

### AC7: UTF-8 and Special Characters in Commit Messages
**Given** commit messages with emoji, non-ASCII characters, special encoding
**When** parsing commit history
**Then** system:
- Correctly handles UTF-8 encoded messages
- Extracts meaningful content from first line of message
- Limits output to first 100 characters per message
- Skips merge commits if they have generic messages

### AC8: Development Activity Pattern Analysis
**Given** extracted commit data
**When** analyzing activity patterns
**Then** system records:
- Whether repository is actively maintained (commits in last 30 days)
- Whether primary language matches Git history patterns (for later use)
- Development velocity (commits per week over project lifetime)
- Time since last commit

---

## Technical Requirements (from Architecture)

### Git History Analyzer Architecture
- **Component**: Git History Analyzer (P0.3 phase, part of parallel analysis pipeline)
- **Responsibility**: Extract metadata from Git repository for development pattern analysis
- **Pattern**: Safe Git command execution with error handling
- **Integration Point**: Part of Analysis Pipeline orchestration (from Story 2.1 tech_stack.py input)
- **Performance Target**: Complete within 2 seconds (part of 5s analysis budget)
- **Dependencies**: ProjectTypeDetector from Story 2.1 (knows project language context)

### Architecture Compliance Patterns
- **Async Execution**: This analyzer runs in parallel with tech_stack and project_files analyzers
- **Timeout Enforcement**: Must use time.perf_counter() with 2-second timeout (from Story 1.4 system)
- **Error Classification**: Errors should not crash pipeline - return None/empty result
- **Logging**: Use standard logging module (no print statements)
- **File Structure**: `src/prompt_enhancement/pipeline/git_history.py`

### Integration with Story 2.1-2.2 Output
Story 2.3 receives output from Stories 2.1-2.2:
```python
# From Story 2.1 (ProjectTypeDetector)
result_2_1: ProjectTypeDetectionResult = {
    primary_language: ProjectLanguage.PYTHON,
    version: "3.9",
    confidence: 0.95,
    ...
}

# From Story 2.2 (ProjectIndicatorFilesDetector)
result_2_2: ProjectIndicatorResult = {
    metadata: ProjectMetadata(...),
    files_found: [...],
    lock_files_present: {...},
    ...
}

# Story 2.3 uses project_path as input
# Returns GitHistoryResult for downstream analysis
detector_2_3 = GitHistoryDetector(
    project_root=project_path,
    detected_language=result_2_1.primary_language,  # Optional context
    max_commits=100  # Configurable, default from architecture
)
result_2_3 = detector_2_3.extract_git_history()
```

### Project Structure Compliance
```
src/prompt_enhancement/
├── pipeline/
│   ├── tech_stack.py           # From Story 2.1
│   ├── project_files.py        # From Story 2.2
│   └── git_history.py          # NEW: GitHistoryDetector implementation
```

### Naming Conventions (from Architecture)
- **Classes**: PascalCase (e.g., `GitHistoryDetector`, `GitHistoryResult`)
- **Functions**: snake_case (e.g., `extract_git_history()`, `read_recent_commits()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_MAX_COMMITS`, `GIT_LOG_FORMAT`)
- **Variables**: snake_case (e.g., `commit_count`, `primary_contributor`)

### Error Handling Requirements
- **Non-critical component**: Git failures should NOT crash pipeline
- **Graceful degradation**: Return empty result (None or empty fields)
- **Permission handling**: Catch `PermissionError`, `FileNotFoundError` gracefully
- **Subprocess errors**: Catch subprocess.CalledProcessError, return None
- **Timeout enforcement**: Use perf_counter() to enforce 2-second limit
- **Logging**: Log at DEBUG level for non-fatal issues, not to user-facing output

### Performance Budget
- **Total time**: 2 seconds (parallel with tech_stack and project_files)
- **Reading last 100 commits**: < 500ms (typical)
- **Parsing and analysis**: < 500ms
- **Buffer**: 1000ms for large repos or slow systems

---

## Data Structures (Tasks 2.3.1)

### GitHistoryResult Dataclass
```python
@dataclass
class GitHistoryResult:
    """Complete Git history analysis result."""

    git_available: bool              # True if .git exists and readable
    total_commits: Optional[int]     # Total commit count (None if unavailable)
    current_branch: Optional[str]    # Current branch name (e.g., "main", "master")
    recent_commits: List[str]        # Last 10 commit messages/summaries
    contributors: List[str]          # Top 5 contributors by commit count
    commits_per_week: Optional[float]  # Average commits per week
    first_commit_date: Optional[str] # ISO 8601 format
    last_commit_date: Optional[str]  # ISO 8601 format
    repository_age_days: Optional[int]  # Days since first commit
    branch_count: Optional[int]      # Number of branches
    is_actively_maintained: bool     # True if commits in last 30 days
    confidence: float                # 0.0-1.0 confidence in results
```

### ContributorInfo Dataclass (helper)
```python
@dataclass
class ContributorInfo:
    """Information about a project contributor."""

    name: str                        # Contributor name (from git config)
    commit_count: int                # Number of commits by this contributor
    percentage: float                # Percentage of total commits
```

---

## Dev Notes - Critical Context for Implementation

### Key Implementation Details

#### 1. Safe Git Command Execution
```bash
# Safe command for reading recent commits
git log --max-count=100 --format='%h|%an|%ai|%s'

# Safe command for branch info
git rev-parse --abbrev-ref HEAD

# Safe command for commit statistics
git rev-list --all --count

# Safe command for contributor analysis
git shortlog -sn --all --max-count=5
```

**Why these specific formats:**
- `--max-count=100`: Limits output for performance
- `--format='...'`: Structured format for parsing
- `--abbrev-ref HEAD`: Returns symbolic name safely
- `--all`: Analyzes all commits, not just current branch
- `--shortlog -sn`: Efficient contributor counting

#### 2. Subprocess Execution Strategy
```python
import subprocess
import time

def _run_git_command(command: List[str], timeout_sec: float = 2.0) -> Optional[str]:
    """Execute Git command safely with timeout.

    Args:
        command: Git command as list (e.g., ['git', 'log', ...])
        timeout_sec: Timeout in seconds

    Returns:
        Command output as string, or None if error/timeout
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=self.project_root  # Execute in project directory
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except subprocess.TimeoutExpired:
        logger.debug(f"Git command timeout: {' '.join(command)}")
        return None
    except (OSError, FileNotFoundError) as e:
        logger.debug(f"Git not available or command failed: {e}")
        return None
    except Exception as e:
        logger.debug(f"Unexpected error running git command: {e}")
        return None
```

#### 3. Checking Git Availability
```python
def _check_git_available(self) -> bool:
    """Check if Git repository exists and is readable."""
    git_dir = self.project_root / '.git'
    if not git_dir.exists():
        return False

    try:
        # Quick test: try to get current branch
        result = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            timeout=1.0,
            cwd=self.project_root
        )
        return result.returncode == 0
    except:
        return False
```

#### 4. Parsing Commit History
```python
def _parse_recent_commits(self, log_output: str) -> List[str]:
    """Extract recent commit messages from git log output.

    Expected format: 'hash|author|date|message'
    Return: List of formatted message strings (first 10)
    """
    commits = []
    if not log_output:
        return commits

    for line in log_output.split('\n')[:10]:  # Limit to 10
        if not line.strip():
            continue

        try:
            parts = line.split('|')
            if len(parts) >= 4:
                hash_short = parts[0][:7]
                author = parts[1]
                date = parts[2]
                message = parts[3]

                # Clean message: take first line, limit length
                message_clean = message.split('\n')[0][:100]

                # Skip merge commits with generic messages
                if message.startswith('Merge ') and len(message) < 30:
                    continue

                commits.append(message_clean)
        except Exception as e:
            logger.debug(f"Error parsing commit line: {e}")
            continue

    return commits
```

#### 5. Computing Development Statistics
```python
def _calculate_statistics(self, log_output: str) -> dict:
    """Calculate development statistics from git log output."""
    from datetime import datetime, timedelta

    stats = {
        'total_commits': 0,
        'first_commit_date': None,
        'last_commit_date': None,
        'commits_per_week': None,
        'repository_age_days': None,
        'is_actively_maintained': False
    }

    if not log_output:
        return stats

    lines = log_output.strip().split('\n')
    if not lines:
        return stats

    try:
        # Get total count (use separate command)
        count_result = self._run_git_command(['git', 'rev-list', '--all', '--count'])
        stats['total_commits'] = int(count_result) if count_result else 0

        # Parse dates from log output
        all_dates = []
        for line in lines:
            try:
                parts = line.split('|')
                if len(parts) >= 3:
                    date_str = parts[2]
                    # Parse ISO format: '2025-12-18 10:30:45 +0000'
                    date_obj = datetime.fromisoformat(date_str.replace(' +0000', '+00:00'))
                    all_dates.append(date_obj)
            except:
                continue

        if all_dates:
            # First and last dates
            all_dates.sort()
            stats['first_commit_date'] = all_dates[0].isoformat()
            stats['last_commit_date'] = all_dates[-1].isoformat()

            # Repository age
            age = (all_dates[-1] - all_dates[0]).days
            stats['repository_age_days'] = age if age > 0 else 1

            # Commits per week
            weeks = max(age / 7, 1)
            stats['commits_per_week'] = stats['total_commits'] / weeks

            # Check if actively maintained (commits in last 30 days)
            now = datetime.now(all_dates[-1].tzinfo)
            last_30_days = now - timedelta(days=30)
            stats['is_actively_maintained'] = all_dates[-1] > last_30_days

    except Exception as e:
        logger.debug(f"Error calculating statistics: {e}")

    return stats
```

#### 6. Extracting Contributors
```python
def _parse_contributors(self, shortlog_output: str) -> List[str]:
    """Parse git shortlog output to get top contributors.

    Format: '  5  John Doe'
    Return: List of contributor names (top 5)
    """
    contributors = []
    if not shortlog_output:
        return contributors

    for line in shortlog_output.split('\n'):
        if not line.strip():
            continue

        try:
            # Format: 'count  name'
            parts = line.strip().split(maxsplit=1)
            if len(parts) == 2 and parts[0].isdigit():
                name = parts[1]
                # Remove email if present
                if '<' in name:
                    name = name.split('<')[0].strip()
                contributors.append(name)
        except:
            continue

    return contributors[:5]  # Limit to top 5
```

### From Story 2.1 Implementation Patterns
**Key Patterns to Follow:**
- Use dataclasses with type hints for result structures
- Implement timeout with `time.perf_counter()`
- Return None or empty result on errors (no exceptions)
- Use logging.debug() for non-fatal issues
- Root-only directory scanning (no recursion)
- Confidence scoring (0.0-1.0) based on data completeness

**Testing Approach from Story 2.1:**
- Create test fixtures with temporary Git repositories
- Test with real git command execution (not mocking)
- Test error cases explicitly (missing .git, permission errors)
- Achieve 95%+ code coverage
- Test within performance budgets

### Git-Specific Considerations

#### A. Detecting Git Repository
```python
# Before running any git commands, check if .git exists
if not (self.project_root / '.git').exists():
    return GitHistoryResult(git_available=False, ...)
```

#### B. Handling Large Repositories
The architecture specifies:
- Read only last 100 commits (not entire history)
- Use `git log --max-count=100` for efficiency
- Complete within 2-second timeout even for 100,000+ commit repos
- Typical GitHub projects: 500-5000 commits → <100ms

#### C. Handling Detached HEAD
Some projects may have detached HEAD state:
```bash
# Instead of just current branch, check state
git rev-parse --abbrev-ref HEAD
# Returns "HEAD" if detached
# Returns "main", "master", etc. if attached
```

#### D. Handling Multiple Git Remotes
- Use `--all` flag to analyze entire repository
- Don't assume "origin" exists (some repos have custom remotes)
- Focus on local commit history (don't fetch from remote)

### Latest Technical Information (2025-12-18)

#### Git Command Best Practices
- **Modern default branch**: `main` (was `master`, now `main` is standard)
- **Safe extraction**: Use format strings, never parse raw output
- **UTF-8 handling**: Git defaults to UTF-8, Python subprocess handles it
- **Large repos**: `git log` with `--max-count` is efficient even on large repos (no loading entire history)
- **Performance**: Git commands on local repository are typically <100ms for most operations

#### Claude Code Environment Considerations
- Git should be available in Claude Code environment
- May need to handle case where project root is not a git repo
- No need to handle authentication (read-only local operations)
- `.git` directory should be accessible (part of project root)

#### Commit Message Standards
- First line is summary (should be <80 characters)
- Can contain emoji (e.g., 🚀, ✨, 🐛, 🔥)
- May contain conventional commits format: `type(scope): message`
- Examples: "feat: Add user authentication", "fix(bug): Handle null pointer"

---

## Developer Context - Previous Story Learnings

### From Story 2.1 (Tech Stack Detection)
**Key Patterns to Follow:**
- Use dataclasses for result structures (highly reusable)
- Implement class-level constants for configuration
- Timeout enforcement using `time.perf_counter()`
- Root-only directory scanning (no recursion into subdirectories)
- Confidence scoring with clear methodology
- Error handling: return None/empty result, log debug info

**Testing Approach:**
- Create temporary test fixtures
- Test with realistic data structures
- Test all error conditions explicitly
- Achieve 95%+ code coverage
- Test within performance timeouts

**Code Quality:**
- Google-style docstrings with full parameters/returns
- Type hints on all functions (including Optional and Union)
- Clear method organization with helper methods
- Graceful error handling with logging
- No external exceptions to caller

### From Story 2.2 (Project Indicator Files)
**Relevant Patterns:**
- Language-specific behavior is handled in separate methods
- Safe file reading with encoding fallback (UTF-8 → latin-1)
- Integration with Story 2.1 output (ProjectLanguage enum)
- Confidence calculation based on evidence available
- Lock file detection patterns (helpful for understanding project maturity)

### Integration Points
Story 2.3 has these integration dependencies:
1. **Story 2.1 Input**: `ProjectLanguage` enum (for context)
2. **Story 2.2 Input**: `ProjectMetadata` (for project understanding)
3. **Story 1.4 System**: `PerformanceTracker` (optional, can use for monitoring)
4. **Architecture**: Async parallel execution in pipeline

---

## Latest Technical Information (2025-12-18)

### Git Command Efficiency
- `git log --max-count=100`: Returns 100 most recent commits, very fast
- `git rev-parse --abbrev-ref HEAD`: Gets current branch efficiently
- `git shortlog -sn`: Counts commits by author efficiently
- `git rev-list --all --count`: Gets total commit count without loading history

### UTF-8 and Encoding Handling
- Python subprocess.run() with `text=True` automatically handles UTF-8
- Git output is UTF-8 by default in modern systems
- Emoji and special characters are safe to handle

### Subprocess Safety
- Always use `capture_output=True` to prevent deadlocks
- Use `text=True` for string output (not bytes)
- Use `timeout` parameter for safety
- Use `cwd` parameter to run in project directory

---

## Completion Status

**Status**: ready-for-dev
**Ready for Development**: Yes ✅

This story has been analyzed exhaustively:
- ✅ Requirements extracted from Epic 2.3
- ✅ Architecture constraints identified
- ✅ Previous implementation patterns studied (Stories 2.1-2.2)
- ✅ Git-specific technical details documented
- ✅ Subprocess and safety patterns documented
- ✅ Error handling strategy defined
- ✅ Test strategy defined
- ✅ Data structures designed
- ✅ Performance budget allocated (2 seconds)
- ✅ Developer implementation guide complete

**Development can begin immediately.** All context provided for flawless implementation.

---

## Dev Agent Record

### Implementation Summary

**Story 2.3 Implementation - TDD Approach (RED → GREEN → REFACTOR)**

#### Test Suite (RED Phase)
- Created comprehensive test file: `tests/test_pipeline/test_git_history.py` (600+ lines)
- **20 test cases** covering all 8 acceptance criteria:
  - Data structure validation (GitHistoryResult, ContributorInfo)
  - Git repository detection and basic analysis (AC1)
  - Recent commit extraction (AC2)
  - Development statistics calculation (AC3)
  - Large repository handling with max_commits limit (AC4)
  - Graceful error handling for non-Git projects (AC5)
  - Permission-denied error handling (AC6)
  - UTF-8 and special character support (AC7)
  - Activity pattern analysis (AC8)
  - Integration tests with realistic projects

#### Implementation (GREEN Phase)
- Created `src/prompt_enhancement/pipeline/git_history.py` (500+ lines)
- **GitHistoryDetector class** with safe Git command execution
- **GitHistoryResult dataclass** for structured results
- **Key Features Implemented:**
  - Git availability detection with .git directory check
  - Safe subprocess execution with timeout enforcement (2-second budget)
  - Recent commit parsing with UTF-8 support
  - Commit author/contributor extraction (top 5)
  - Development statistics calculation:
    - Total commits and commit frequency (per week)
    - Repository age in days
    - First/last commit dates with ISO 8601 format
    - Active maintenance detection (30-day threshold)
  - Graceful degradation for non-Git projects
  - Error handling with logging (no crashes on permission errors)
  - Performance optimization (respects max_commits, completes <2 seconds)
  - Confidence scoring based on data completeness

#### REFACTOR Phase (Code Quality)
- Fixed date parsing to handle git log timezone format
- Improved error handling with specific exception catching
- Added comprehensive logging throughout
- Ensured performance targets met
- Verified integration with Stories 2.1-2.2 patterns

#### Test Results
- **20/20 tests PASSING** ✅
- **85/85 total pipeline tests PASSING** (20 new + 65 existing) ✅
- **Zero regressions** in existing tests
- All acceptance criteria validated through tests

### File List

#### New Files Created
- `src/prompt_enhancement/pipeline/git_history.py` - Main implementation (500 lines)
- `tests/test_pipeline/test_git_history.py` - Comprehensive test suite (600 lines)

#### Modified Files
- `docs/sprint-status.yaml` - Updated Story 2.3 status to "review"
- `docs/stories/2-3-extract-git-history-and-project-context.md` - Updated story status and completion notes

### Completion Notes

✅ **All Acceptance Criteria Met:**
- AC1: Git repository detection ✓
- AC2: Recent commit analysis ✓
- AC3: Git statistics and development patterns ✓
- AC4: Large repository handling (<2s timeout) ✓
- AC5: Graceful degradation for non-Git projects ✓
- AC6: Permission error handling ✓
- AC7: UTF-8 and special character support ✓
- AC8: Development activity pattern analysis ✓

✅ **Quality Standards:**
- All 20 tests passing (100%)
- No regressions (85 total tests passing)
- Code follows architecture patterns from Stories 2.1-2.2
- Performance targets met (timeout <2 seconds)
- Comprehensive error handling with logging
- Type hints and docstrings throughout

✅ **Integration Ready:**
- Properly integrates with Story 2.1 (ProjectLanguage enum)
- Compatible with Story 2.2 patterns
- Ready for Story 2.4 (fingerprinting) integration
- Ready for parallel async execution in analysis pipeline

---

## References

- [Epic 2 Overview](docs/epics.md#Epic-2-Automatic-Project--Standards-Analysis)
- [Story 2.3 Definition](docs/epics.md#Story-23-Extract-Git-History-and-Project-Context)
- [Story 2.1 Implementation](docs/stories/2-1-detect-project-type-from-filesystem-markers.md)
- [Story 2.2 Implementation](docs/stories/2-2-identify-project-indicator-files.md)
- [Architecture: Analysis Pipeline](docs/architecture.md#Analysis-Pipeline)
- [Architecture: Git History Analyzer](docs/architecture.md#Key-Architecture-Decisions)
- [PRD: Automatic Project Detection](docs/prd.md#Automatic-Project-Detection)
- [Story 1.4: Performance System](docs/stories/1-4-implement-5-15-second-performance-target.md)
