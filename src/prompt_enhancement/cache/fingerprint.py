"""
Project Fingerprint Generator - Story 2.4.

Generates deterministic fingerprints of projects for cache validation.
Combines package files, lock files, Git metadata, and language/version information.

Safe execution with graceful degradation for non-Git projects.
Ensures cache hits only when projects are unchanged.
"""

import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from prompt_enhancement.pipeline.tech_stack import ProjectTypeDetectionResult
from prompt_enhancement.pipeline.project_files import ProjectIndicatorResult
from prompt_enhancement.pipeline.git_history import GitHistoryResult


logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class FingerprintComponents:
    """Individual component hashes that compose the full fingerprint."""

    package_files_hash: str
    lock_files_hash: str
    git_metadata_hash: str
    language_version_hash: str
    total_hash: str


@dataclass
class FingerprintInfo:
    """Complete fingerprint information with metadata."""

    fingerprint: str  # Hexadecimal string (40+ chars)
    algorithm: str  # "sha256"
    timestamp: str  # ISO format timestamp
    version: int  # Current version (1)
    components: FingerprintComponents  # Individual component hashes
    file_count: int  # Number of files hashed

    @property
    def __dict__(self) -> dict:
        """Return JSON-serializable dictionary with nested dataclasses converted."""
        return {
            "fingerprint": self.fingerprint,
            "algorithm": self.algorithm,
            "timestamp": self.timestamp,
            "version": self.version,
            "components": asdict(self.components),
            "file_count": self.file_count,
        }


# ============================================================================
# FingerprintGenerator Class
# ============================================================================


class FingerprintGenerator:
    """
    Generates deterministic fingerprints of projects for cache validation.

    Combines:
    - Package files (package.json, requirements.txt, etc.)
    - Lock files (package-lock.json, Pipfile.lock, etc.)
    - Git metadata (commit count, branch, last commit date)
    - Language/version information

    Attributes:
        project_root: Root directory of the project
        timeout_sec: Timeout for fingerprint generation (default 1.0)
        max_files: Maximum files to hash (default 100)
    """

    DEFAULT_TIMEOUT_SEC = 1.0
    MAX_FILES = 100
    FINGERPRINT_VERSION = 1
    FINGERPRINT_ALGORITHM = "sha256"

    def __init__(
        self,
        project_root: Path,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        max_files: int = MAX_FILES,
    ):
        """
        Initialize fingerprint generator.

        Args:
            project_root: Root directory to fingerprint
            timeout_sec: Timeout for generation (default 1.0 seconds)
            max_files: Maximum files to process (default 100)
        """
        self.project_root = Path(project_root)
        self.timeout_sec = timeout_sec
        self.max_files = max_files
        self.start_time = time.perf_counter()

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def generate_fingerprint(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
        git_result: GitHistoryResult,
    ) -> Optional[FingerprintInfo]:
        """
        Generate project fingerprint from analysis results.

        AC1: Generate fingerprints from package files
        AC2: Include Git metadata
        AC3: Include language/framework information
        AC4: Ensure fingerprints are deterministic
        AC5: Detect file changes
        AC6: Cache validation with matching fingerprints
        AC7: Complete within 1 second budget
        AC8: Valid fingerprint format with version

        Args:
            tech_result: Tech stack detection result (Story 2.1)
            files_result: Project indicator result (Story 2.2)
            git_result: Git history result (Story 2.3)

        Returns:
            FingerprintInfo with complete fingerprint and metadata, or None on timeout
        """
        try:
            # Check timeout
            if self._is_timeout():
                logger.warning("Fingerprint generation timeout")
                return None

            # Generate component hashes
            package_files_hash = self._hash_package_files(files_result)
            lock_files_hash = self._hash_lock_files(files_result)
            git_metadata_hash = self._hash_git_metadata(git_result)
            language_version_hash = self._hash_language_version(tech_result, files_result)

            # Combine all hashes
            combined_data = f"{package_files_hash}|{lock_files_hash}|{git_metadata_hash}|{language_version_hash}"
            total_hash = hashlib.sha256(combined_data.encode("utf-8")).hexdigest()

            # Count files
            file_count = len(files_result.files_found) if files_result.files_found else 0

            # Create components
            components = FingerprintComponents(
                package_files_hash=package_files_hash,
                lock_files_hash=lock_files_hash,
                git_metadata_hash=git_metadata_hash,
                language_version_hash=language_version_hash,
                total_hash=total_hash,
            )

            # Create fingerprint info
            fingerprint_info = FingerprintInfo(
                fingerprint=total_hash,  # Use total hash as the fingerprint
                algorithm=self.FINGERPRINT_ALGORITHM,
                timestamp=datetime.now(timezone.utc).isoformat(),
                version=self.FINGERPRINT_VERSION,
                components=components,
                file_count=file_count,
            )

            return fingerprint_info

        except Exception as e:
            logger.error(f"Error generating fingerprint: {e}", exc_info=True)
            return None

    # ========================================================================
    # Component Hashing
    # ========================================================================

    def _hash_package_files(self, files_result: ProjectIndicatorResult) -> str:
        """
        Hash package files for deterministic fingerprinting.

        AC1: Generate fingerprints from package files
        AC4: Ensure fingerprints are deterministic

        Args:
            files_result: Project indicator result with list of files found

        Returns:
            SHA256 hash of package files in sorted order
        """
        if not files_result or not files_result.files_found:
            return hashlib.sha256(b"no-package-files").hexdigest()

        try:
            # Collect hashes of package files
            file_hashes = []

            for file_path in sorted(files_result.files_found):
                full_path = self.project_root / file_path

                # Only hash files that exist and are readable
                if not full_path.exists() or not full_path.is_file():
                    continue

                try:
                    # Read file content
                    file_content = full_path.read_bytes()

                    # Hash file content
                    file_hash = hashlib.sha256(file_content).hexdigest()

                    # Store as "filename:hash"
                    file_hashes.append(f"{file_path}:{file_hash}")

                except (OSError, IOError) as e:
                    logger.debug(f"Could not read file {file_path}: {e}")
                    continue

            if not file_hashes:
                return hashlib.sha256(b"no-readable-files").hexdigest()

            # Combine in sorted order for determinism
            combined = "|".join(file_hashes)
            return hashlib.sha256(combined.encode("utf-8")).hexdigest()

        except Exception as e:
            logger.debug(f"Error hashing package files: {e}")
            return hashlib.sha256(b"error-hashing-files").hexdigest()

    def _hash_lock_files(self, files_result: ProjectIndicatorResult) -> str:
        """
        Hash lock files for cache validation.

        AC1: Lock files are part of fingerprinting
        AC4: Ensure deterministic output

        Args:
            files_result: Project indicator result with lock files

        Returns:
            SHA256 hash of lock files
        """
        if not files_result or not files_result.lock_files_present:
            return hashlib.sha256(b"no-lock-files").hexdigest()

        try:
            # Collect hashes of lock files
            lock_hashes = []

            for lock_file in sorted(files_result.lock_files_present):
                full_path = self.project_root / lock_file

                # Only hash lock files that exist
                if not full_path.exists() or not full_path.is_file():
                    continue

                try:
                    # Read lock file content
                    file_content = full_path.read_bytes()

                    # Hash file content
                    file_hash = hashlib.sha256(file_content).hexdigest()

                    # Store as "filename:hash"
                    lock_hashes.append(f"{lock_file}:{file_hash}")

                except (OSError, IOError) as e:
                    logger.debug(f"Could not read lock file {lock_file}: {e}")
                    continue

            if not lock_hashes:
                return hashlib.sha256(b"no-lock-files").hexdigest()

            # Combine in sorted order for determinism
            combined = "|".join(lock_hashes)
            return hashlib.sha256(combined.encode("utf-8")).hexdigest()

        except Exception as e:
            logger.debug(f"Error hashing lock files: {e}")
            return hashlib.sha256(b"error-hashing-locks").hexdigest()

    def _hash_git_metadata(self, git_result: GitHistoryResult) -> str:
        """
        Hash Git metadata for cache validation.

        AC2: Include Git metadata in fingerprint
        AC4: Deterministic output for same Git state

        Args:
            git_result: Git history result from Story 2.3

        Returns:
            SHA256 hash of Git metadata
        """
        if not git_result or not git_result.git_available:
            # Non-Git projects get consistent hash
            return hashlib.sha256(b"no-git").hexdigest()

        try:
            # Build metadata string from Git information
            # Use only immutable data (no timestamps)
            metadata_parts = [
                f"commits:{git_result.total_commits or 0}",
                f"branch:{git_result.current_branch or 'unknown'}",
                f"contributors:{len(git_result.contributors or [])}",
                f"branches:{git_result.branch_count or 0}",
                f"maintained:{git_result.is_actively_maintained}",
            ]

            metadata_str = "|".join(metadata_parts)
            return hashlib.sha256(metadata_str.encode("utf-8")).hexdigest()

        except Exception as e:
            logger.debug(f"Error hashing Git metadata: {e}")
            return hashlib.sha256(b"error-git-metadata").hexdigest()

    def _hash_language_version(
        self,
        tech_result: ProjectTypeDetectionResult,
        files_result: ProjectIndicatorResult,
    ) -> str:
        """
        Hash language and framework information.

        AC3: Include language/framework context in fingerprint
        AC4: Deterministic output for same language/version

        Args:
            tech_result: Tech stack detection from Story 2.1
            files_result: Project indicator result from Story 2.2

        Returns:
            SHA256 hash of language/version information
        """
        try:
            # Build language context string
            language_parts = []

            # Primary language and version
            if tech_result and tech_result.primary_language:
                language_parts.append(f"lang:{tech_result.primary_language.value}")
                if tech_result.version:
                    language_parts.append(f"version:{tech_result.version}")

            # Secondary languages
            if tech_result and tech_result.secondary_languages:
                secondary = ",".join(lang.value for lang in tech_result.secondary_languages)
                language_parts.append(f"secondary:{secondary}")

            # Package manager
            if files_result and files_result.metadata:
                language_parts.append(f"manager:{files_result.metadata.package_manager or 'unknown'}")

            if not language_parts:
                return hashlib.sha256(b"no-language-info").hexdigest()

            language_str = "|".join(language_parts)
            return hashlib.sha256(language_str.encode("utf-8")).hexdigest()

        except Exception as e:
            logger.debug(f"Error hashing language/version: {e}")
            return hashlib.sha256(b"error-language-hash").hexdigest()

    # ========================================================================
    # Cache Validation
    # ========================================================================

    def validate_cache(
        self,
        current_fingerprint: FingerprintInfo,
        cached_fingerprint: FingerprintInfo,
        cache_timestamp: datetime,
        ttl_hours: int = 24,
    ) -> bool:
        """
        Validate cache based on fingerprint matching and TTL.

        AC6: Cache validation with matching fingerprints
        AC7: Performance-conscious validation

        Args:
            current_fingerprint: Currently generated fingerprint
            cached_fingerprint: Previously cached fingerprint
            cache_timestamp: When the cache was created
            ttl_hours: Time-to-live in hours (default 24)

        Returns:
            True if cache is valid (fingerprints match and TTL not exceeded)
        """
        try:
            # Check if fingerprints match
            if current_fingerprint.fingerprint != cached_fingerprint.fingerprint:
                logger.debug("Cache invalid: fingerprint mismatch")
                return False

            # Check if TTL has expired
            now = datetime.now(timezone.utc)

            # Ensure cache_timestamp is timezone-aware
            if cache_timestamp.tzinfo is None:
                cache_timestamp = cache_timestamp.replace(tzinfo=timezone.utc)

            # Calculate age
            cache_age = now - cache_timestamp
            ttl_delta = timedelta(hours=ttl_hours)

            if cache_age > ttl_delta:
                logger.debug(f"Cache invalid: TTL expired ({cache_age.total_seconds():.1f}s > {ttl_delta.total_seconds():.1f}s)")
                return False

            logger.debug("Cache valid: fingerprint match and TTL OK")
            return True

        except Exception as e:
            logger.error(f"Error validating cache: {e}", exc_info=True)
            return False

    # ========================================================================
    # Timeout Management
    # ========================================================================

    def _is_timeout(self) -> bool:
        """Check if timeout has been exceeded."""
        elapsed = time.perf_counter() - self.start_time
        return elapsed > self.timeout_sec
