# Story 2.4: Generate Project Fingerprint for Caching

**Story ID**: 2.4
**Epic**: Epic 2 - Automatic Project & Standards Analysis
**Status**: ready-for-dev
**Created**: 2025-12-18

---

## Story

As a **system ensuring consistent detection across runs**,
I want **to generate a unique fingerprint of the project**,
So that **I can validate cache and ensure same project always gets same analysis**.

---

## Acceptance Criteria

### AC1: Fingerprint Generation from Package Files
**Given** a project with package/configuration files
**When** computing project fingerprint
**Then** system creates hash from:
- Package files (package.json, requirements.txt, pyproject.toml, go.mod, Cargo.toml, pom.xml, .csproj)
- Lock files (package-lock.json, poetry.lock, Cargo.lock, etc.)
**And** fingerprint is deterministic (same project always produces same fingerprint)

### AC2: Git Metadata in Fingerprint
**Given** project is Git-tracked
**When** computing fingerprint
**Then** fingerprint includes:
- Git log count (total commits)
- Repository initialization date
**And** for non-Git projects, uses 0 or skips Git component

### AC3: Language and Framework Context
**Given** project analysis results available
**When** generating fingerprint
**Then** fingerprint incorporates:
- Detected primary language (from Story 2.1)
- Major dependency versions (from Story 2.2)
- Repository metadata (from Story 2.3)
**And** includes framework/version information for deterministic detection

### AC4: Fingerprint Determinism
**Given** same project analyzed multiple times
**When** fingerprints generated
**Then**:
- Fingerprint is identical across runs (deterministic hash)
- Byte-for-byte consistent hashing algorithm
- Does NOT include timestamps, random data, or volatile information
- File order is canonical (alphabetical or sorted)

### AC5: Fingerprint Change Detection
**Given** project files modified
**When** project re-analyzed
**Then**:
- Fingerprint changes (detects modification)
- Cache invalidation triggered
- Re-analysis forced (old cache not used)
**And** single file change produces detectable fingerprint change

### AC6: Cache Validation with Fingerprint
**Given** cache exists from previous analysis
**When** checking if cache valid
**Then** system:
- Compares stored fingerprint with newly computed fingerprint
- Checks TTL (24-hour default)
- Uses cache ONLY if both fingerprints match AND TTL valid
- Invalidates cache if fingerprints differ

### AC7: Large Repository Handling
**Given** repository with thousands of files
**When** computing fingerprint
**Then**:
- Does NOT need to read all files (too expensive)
- Uses efficient hashing of key files only
- Completes within timeout budget
- Maintains accuracy (changes to key files detected)

### AC8: Fingerprint Format and Consistency
**Given** fingerprint computed
**When** storing/comparing
**Then**:
- Fingerprint is hexadecimal string (40+ characters)
- Format is JSON-serializable
- Includes version field (for future algorithm changes)
- Backward compatible with previous versions

---

## Technical Requirements (from Architecture)

### Project Fingerprinting Architecture
- **Component**: Fingerprint Generator (P0.2 phase, part of cache management system)
- **Responsibility**: Generate deterministic project fingerprint for cache validation
- **Pattern**: Hash-based fingerprinting with file content and metadata
- **Integration Point**: Cache validation in pipeline orchestration
- **Performance Target**: Complete within 1 second
- **Dependencies**: Results from Stories 2.1 (tech_stack), 2.2 (project_files), 2.3 (git_history)

### Architecture Caching Strategy
From architecture.md, caching uses three tiers:
```
L1: Memory (functools.lru_cache) - 5 min
L2: File (~/.prompt-enhancement/cache.json) - 24 hours
L3: Redis (optional) - Configurable

Fingerprint validates cache consistency at L2 level
```

### Cache Validation Flow
```
1. Compute project fingerprint (this story)
2. Check L1 (memory cache) - if hit, return cached result
3. Check L2 (file cache) if exists:
   - Load stored fingerprint from cache metadata
   - Compare: new_fingerprint == stored_fingerprint?
   - Check: current_time - cache_time < 24_hours?
   - If both True: use cached result
   - If False: invalidate cache, re-analyze
4. Store result with fingerprint and timestamp
```

### Project Structure Compliance
```
src/prompt_enhancement/
├── pipeline/
│   ├── tech_stack.py           # From Story 2.1
│   ├── project_files.py        # From Story 2.2
│   ├── git_history.py          # From Story 2.3
│   └── analyzer.py             # Orchestrator, calls fingerprint gen
├── cache/
│   ├── fingerprint.py          # NEW: FingerprintGenerator
│   ├── manager.py              # Cache manager using fingerprint
│   ├── memory.py
│   └── persistent.py
```

### Naming Conventions (from Architecture)
- **Classes**: PascalCase (e.g., `FingerprintGenerator`, `FingerprintInfo`)
- **Functions**: snake_case (e.g., `generate_fingerprint()`, `validate_cache()`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_HASH_ALGORITHM`, `CACHE_TTL_HOURS`)
- **Variables**: snake_case (e.g., `fingerprint_hash`, `cache_valid`)

### Error Handling Requirements
- **Non-critical component**: Fingerprint generation failures should not crash
- **Graceful degradation**: Return None or simple fallback fingerprint
- **File access errors**: Skip missing files, use available files only
- **Performance**: Must complete within 1 second even for large repos
- **Logging**: Debug level for non-fatal issues

### Performance Budget
- **Total time**: 1 second (not in parallel, called once per analysis)
- **File hashing**: < 500ms (even with large files)
- **Metadata collection**: < 200ms
- **Hash computation**: < 300ms
- **Buffer**: For network/slow systems

---

## Data Structures (Tasks 2.4.1)

### FingerprintInfo Dataclass
```python
@dataclass
class FingerprintInfo:
    """Project fingerprint for cache validation."""

    fingerprint: str              # Hexadecimal hash (40+ chars)
    algorithm: str                # "sha256" or algorithm version
    timestamp: str                # ISO 8601 creation time
    version: int                  # Format version (current=1)
    components: FingerprintComponents  # Breakdown of fingerprint components
    file_count: int              # Number of files included
```

### FingerprintComponents Dataclass
```python
@dataclass
class FingerprintComponents:
    """Breakdown of fingerprint computation."""

    package_files_hash: str      # Hash of all package/config files
    lock_files_hash: str         # Hash of lock files
    git_metadata_hash: str       # Hash of git info (or empty)
    language_version_hash: str   # Hash of detected language + version
    total_hash: str              # Final combined hash
```

---

## Dev Notes - Critical Context for Implementation

### Key Implementation Details

#### 1. File Hashing Strategy
```python
import hashlib
from pathlib import Path

def _compute_file_hash(file_path: Path) -> str:
    """Compute SHA256 hash of file contents.

    Args:
        file_path: Path to file to hash

    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    # Read in chunks for memory efficiency
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()
```

**Why SHA256:**
- Cryptographically strong (collision resistant)
- Fast and efficient
- Standard format (easy to compare)
- 64-character hex output (identifiable)
- Python built-in support

#### 2. Multi-Component Fingerprinting
```python
def generate_fingerprint(
    self,
    project_path: Path,
    detection_result: ProjectTypeDetectionResult,
    metadata_result: ProjectIndicatorResult,
    git_result: GitHistoryResult
) -> FingerprintInfo:
    """Generate project fingerprint from all analysis results.

    Combines multiple components for comprehensive fingerprinting:
    1. Package/config file hashes
    2. Lock file hashes
    3. Git metadata
    4. Detected language/version
    """
    sha256 = hashlib.sha256()

    # Component 1: Package files (config files discovered)
    package_hash = self._hash_files(
        project_path,
        detection_result.markers_found  # From Story 2.1
    )
    sha256.update(package_hash.encode())

    # Component 2: Lock files (from Story 2.2)
    lock_hash = self._hash_files(
        project_path,
        metadata_result.lock_files_present
    )
    sha256.update(lock_hash.encode())

    # Component 3: Git metadata (from Story 2.3)
    git_hash = self._hash_git_metadata(git_result)
    sha256.update(git_hash.encode())

    # Component 4: Language and version context
    language_hash = hashlib.sha256(
        f"{detection_result.primary_language.value}_{detection_result.version}".encode()
    ).hexdigest()[:16]
    sha256.update(language_hash.encode())

    # Final hash
    final_fingerprint = sha256.hexdigest()

    return FingerprintInfo(
        fingerprint=final_fingerprint,
        algorithm="sha256",
        timestamp=datetime.now(timezone.utc).isoformat(),
        version=1,
        components=FingerprintComponents(
            package_files_hash=package_hash,
            lock_files_hash=lock_hash,
            git_metadata_hash=git_hash,
            language_version_hash=language_hash,
            total_hash=final_fingerprint
        ),
        file_count=len(detection_result.markers_found) + len(metadata_result.lock_files_present)
    )
```

#### 3. File Collection and Hashing
```python
def _hash_files(self, project_path: Path, file_names: List[str]) -> str:
    """Hash multiple files in deterministic order.

    Args:
        project_path: Project root directory
        file_names: List of filenames to hash

    Returns:
        Combined hash of all files
    """
    sha256 = hashlib.sha256()

    # Sort for deterministic ordering
    sorted_files = sorted(file_names)

    for filename in sorted_files:
        file_path = project_path / filename
        if file_path.exists() and file_path.is_file():
            try:
                # Hash filename + content for robustness
                sha256.update(filename.encode())

                # Hash file content
                file_hash = self._compute_file_hash(file_path)
                sha256.update(file_hash.encode())
            except Exception as e:
                logger.debug(f"Error hashing file {filename}: {e}")
                # Continue with other files
                continue

    return sha256.hexdigest()
```

#### 4. Git Metadata Hashing
```python
def _hash_git_metadata(self, git_result: GitHistoryResult) -> str:
    """Hash Git metadata for fingerprinting.

    Args:
        git_result: Git analysis result from Story 2.3

    Returns:
        Hash of git metadata
    """
    if not git_result or not git_result.git_available:
        return ""

    # Combine key git information
    git_data = ""

    if git_result.total_commits:
        git_data += f"commits:{git_result.total_commits}|"
    if git_result.first_commit_date:
        git_data += f"date:{git_result.first_commit_date}|"
    if git_result.current_branch:
        git_data += f"branch:{git_result.current_branch}|"

    if not git_data:
        return ""

    return hashlib.sha256(git_data.encode()).hexdigest()[:16]
```

#### 5. Cache Validation Logic
```python
def validate_cache(
    self,
    stored_fingerprint: FingerprintInfo,
    current_fingerprint: FingerprintInfo,
    cache_timestamp: datetime,
    ttl_hours: int = 24
) -> bool:
    """Validate if cache should be used based on fingerprint and TTL.

    Args:
        stored_fingerprint: Fingerprint from cache metadata
        current_fingerprint: Newly computed fingerprint
        cache_timestamp: When cache was created
        ttl_hours: Time-to-live in hours (default 24)

    Returns:
        True if cache is valid and should be used
    """
    # Check 1: Fingerprints must match
    if stored_fingerprint.fingerprint != current_fingerprint.fingerprint:
        logger.debug("Cache invalidated: fingerprint mismatch (project changed)")
        return False

    # Check 2: TTL must be valid
    now = datetime.now(timezone.utc)
    cache_age = (now - cache_timestamp).total_seconds() / 3600  # hours
    if cache_age > ttl_hours:
        logger.debug(f"Cache expired: {cache_age:.1f}h > {ttl_hours}h TTL")
        return False

    logger.debug(f"Cache valid: fingerprint match and TTL OK ({cache_age:.1f}h old)")
    return True
```

#### 6. Fingerprint Comparison
```python
def fingerprints_match(
    self,
    fingerprint1: FingerprintInfo,
    fingerprint2: FingerprintInfo
) -> bool:
    """Check if two fingerprints represent same project state.

    Args:
        fingerprint1: First fingerprint
        fingerprint2: Second fingerprint

    Returns:
        True if fingerprints match (project unchanged)
    """
    return (
        fingerprint1.fingerprint == fingerprint2.fingerprint and
        fingerprint1.algorithm == fingerprint2.algorithm and
        fingerprint1.version == fingerprint2.version
    )
```

### From Stories 2.1-2.3 Implementation Patterns
**Key Patterns to Follow:**
- Use dataclasses for result structures
- Implement timeout enforcement (1-second budget)
- Return None/empty on non-critical errors
- Use logging.debug() for diagnostics
- Confidence scoring or quality metrics
- Clear separation of concerns

**Hashing Best Practices:**
- Always sort files for deterministic output
- Include filename in hash (not just content)
- Use SHA256 (standard, fast, secure)
- Handle file read errors gracefully
- Document hash composition clearly

### Cache Integration Points

#### With Story 2.1-2.3 Results
```python
# Pipeline orchestrator will call fingerprint generator:
fingerprint = await fingerprint_generator.generate_fingerprint(
    project_path=Path("/project"),
    detection_result=tech_stack_result,      # From Story 2.1
    metadata_result=project_files_result,    # From Story 2.2
    git_result=git_history_result            # From Story 2.3
)

# Cache manager uses fingerprint:
cache_valid = cache_manager.validate_cache(
    stored_fingerprint=cached_metadata.fingerprint,
    current_fingerprint=fingerprint,
    cache_timestamp=cached_metadata.timestamp
)

if cache_valid:
    return cached_standards  # Use cached analysis
else:
    # Re-analyze and cache with new fingerprint
```

#### With Cache Manager (Story not yet created)
The cache manager (future story) will:
1. Call fingerprint generator before checking cache
2. Store fingerprint with cached data
3. Validate fingerprint + TTL before using cache
4. Invalidate cache if fingerprint changes

---

## Latest Technical Information (2025-12-18)

### Hashing Algorithm Selection
- **SHA256**: Industry standard, fast, cryptographically secure
  - Output: 64-character hex string
  - Speed: ~100-200MB/s on modern hardware
  - Collision resistance: Excellent
- **Alternative (not recommended)**: MD5 - fast but cryptographically weak
- **Alternative (not needed)**: SHA512 - slower, not necessary for this use case

### Deterministic Hashing Requirements
- **File ordering**: Must sort files alphabetically
- **Encoding**: Must use consistent UTF-8 encoding
- **Whitespace**: Include actual file content (don't normalize)
- **Timestamps**: Never include file modification times
- **Random data**: Never include UUIDs or random values

### Cache Invalidation Strategies
Best practice: Multi-factor validation
1. **Content hash** (fingerprint) - detects project changes
2. **TTL** - ensures freshness (24 hours standard)
3. **Version check** - allows algorithm upgrades
4. **Optional**: File modification time (supplementary)

### Performance Optimization
- **For large repos**: Hash only package/lock files, not entire project
- **File size limit**: Skip very large files (> 100MB) if needed
- **Chunked reading**: Always read files in chunks (4KB) for memory efficiency
- **Async hashing**: Can parallelize file hashing if many files

---

## Completion Status

**Status**: ready-for-dev
**Ready for Development**: Yes ✅

This story has been analyzed exhaustively:
- ✅ Requirements extracted from Epic 2.4
- ✅ Architecture constraints identified (3-tier caching, fingerprint validation)
- ✅ Cache validation strategy defined
- ✅ Multi-component fingerprinting architecture designed
- ✅ Data structures created (FingerprintInfo, FingerprintComponents)
- ✅ Hash algorithm selection documented
- ✅ Integration with Stories 2.1-2.3 defined
- ✅ File hashing patterns provided
- ✅ Cache validation logic patterns provided
- ✅ Performance budget allocated (1 second)
- ✅ Error handling strategy defined
- ✅ Latest technical information (SHA256, determinism, cache strategies)

**Development can begin immediately.** All context provided for flawless implementation.

---

## References

- [Epic 2 Overview](docs/epics.md#Epic-2-Automatic-Project--Standards-Analysis)
- [Story 2.4 Definition](docs/epics.md#Story-24-Generate-Project-Fingerprint-for-Caching)
- [Story 2.1: Tech Stack Detection](docs/stories/2-1-detect-project-type-from-filesystem-markers.md)
- [Story 2.2: Project Indicator Files](docs/stories/2-2-identify-project-indicator-files.md)
- [Story 2.3: Git History](docs/stories/2-3-extract-git-history-and-project-context.md)
- [Architecture: Three-Tier Caching Strategy](docs/architecture.md#Key-Architecture-Decisions)
- [Architecture: Performance Time Budget](docs/architecture.md#Key-Architecture-Decisions)
- [PRD: Caching and Consistency](docs/prd.md#Requirements-Inventory)
