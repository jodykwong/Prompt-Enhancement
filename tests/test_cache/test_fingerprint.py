"""
Tests for Project Fingerprint Generator - Story 2.4.

Comprehensive test suite for FingerprintGenerator implementing all acceptance criteria.
"""

import hashlib
import json
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from prompt_enhancement.cache.fingerprint import (
    FingerprintGenerator,
    FingerprintInfo,
    FingerprintComponents,
)
from prompt_enhancement.pipeline.tech_stack import (
    ProjectLanguage,
    ProjectTypeDetectionResult,
)
from prompt_enhancement.pipeline.project_files import (
    ProjectMetadata,
    ProjectIndicatorResult,
)
from prompt_enhancement.pipeline.git_history import GitHistoryResult, CommitInfo  # FIX HIGH #3


class TestFingerprintDataStructures:
    """Test fingerprint data structure validation - AC8."""

    def test_fingerprint_components_creation(self):
        """FingerprintComponents should have all required fields."""
        components = FingerprintComponents(
            package_files_hash="abc123",
            lock_files_hash="def456",
            git_metadata_hash="ghi789",
            language_version_hash="jkl012",
            total_hash="mno345",
        )

        assert components.package_files_hash == "abc123"
        assert components.lock_files_hash == "def456"
        assert components.git_metadata_hash == "ghi789"
        assert components.language_version_hash == "jkl012"
        assert components.total_hash == "mno345"

    def test_fingerprint_info_creation(self):
        """FingerprintInfo should have all required fields - AC8."""
        now = datetime.now(timezone.utc)
        components = FingerprintComponents(
            package_files_hash="abc",
            lock_files_hash="def",
            git_metadata_hash="ghi",
            language_version_hash="jkl",
            total_hash="mno",
        )

        fingerprint = FingerprintInfo(
            fingerprint="1234567890abcdef",
            algorithm="sha256",
            timestamp=now.isoformat(),
            version=1,
            components=components,
            file_count=5,
        )

        assert fingerprint.fingerprint == "1234567890abcdef"
        assert fingerprint.algorithm == "sha256"
        assert fingerprint.version == 1
        assert fingerprint.file_count == 5
        assert len(fingerprint.fingerprint) >= 16

    def test_fingerprint_is_json_serializable(self):
        """FingerprintInfo should be JSON serializable - AC8."""
        components = FingerprintComponents(
            package_files_hash="abc",
            lock_files_hash="def",
            git_metadata_hash="ghi",
            language_version_hash="jkl",
            total_hash="mno",
        )

        fingerprint = FingerprintInfo(
            fingerprint="1234567890abcdef",
            algorithm="sha256",
            timestamp=datetime.now(timezone.utc).isoformat(),
            version=1,
            components=components,
            file_count=5,
        )

        # Should be JSON serializable
        json_str = json.dumps(fingerprint.__dict__)
        assert json_str is not None
        assert "sha256" in json_str


class TestFingerprintGeneration:
    """Test fingerprint generation from project files - AC1, AC4."""

    def test_generate_fingerprint_basic(self):
        """Should generate fingerprint from package files - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package files
            Path(tmpdir, "package.json").write_text('{"name": "test"}')
            Path(tmpdir, "package-lock.json").write_text('{"lockfileVersion": 2}')

            # Create minimal analysis results
            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test-project",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json", "package-lock.json"],
                lock_files_present={"package-lock.json"},
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            assert fingerprint is not None
            assert len(fingerprint.fingerprint) >= 16
            assert fingerprint.algorithm == "sha256"
            assert fingerprint.version == 1

    def test_fingerprint_determinism(self):
        """Should generate identical fingerprint for same project - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create package files
            Path(tmpdir, "package.json").write_text('{"name": "test"}')
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.9",
                confidence=0.95,
                markers_found=["requirements.txt"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version="3.9",
                package_manager="pip",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["requirements.txt"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))

            # Generate twice
            fp1 = generator.generate_fingerprint(tech_result, files_result, git_result)
            fp2 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Should be identical (deterministic)
            assert fp1.fingerprint == fp2.fingerprint
            assert fp1.algorithm == fp2.algorithm
            assert fp1.version == fp2.version

    def test_timestamp_is_metadata_not_part_of_hash(self):
        """
        Timestamp is metadata about fingerprint generation, not part of hash - FIX HIGH #1.

        AC4 requires deterministic hash, but timestamp can differ (it's metadata).
        This test verifies that:
        1. Fingerprint HASH is identical across runs (deterministic)
        2. Timestamp MAY differ (it's metadata about when fingerprint was generated)
        3. Cache validation correctly ignores timestamp (only compares hash)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))

            # Generate first fingerprint
            fp1 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Small delay to ensure different timestamp
            time.sleep(0.01)

            # Generate second fingerprint (same project, different time)
            fp2 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # VERIFY: Fingerprint hash is IDENTICAL (deterministic)
            assert fp1.fingerprint == fp2.fingerprint, "Hash must be deterministic"

            # VERIFY: Timestamp MAY differ (it's metadata, not part of hash)
            # Note: Timestamps will differ if generated at different times
            # This is EXPECTED and CORRECT behavior

            # VERIFY: Cache validation works (ignores timestamp)
            now = datetime.now(timezone.utc)
            cache_timestamp = now - timedelta(hours=1)
            is_valid = generator.validate_cache(fp1, fp2, cache_timestamp)
            assert is_valid is True, "Cache validation must ignore timestamp differences"

    def test_fingerprint_changes_with_file_modification(self):
        """Should detect file changes - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create initial file
            config_file = Path(tmpdir, "package.json")
            config_file.write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))

            # Generate initial fingerprint
            fp1 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Modify file
            config_file.write_text('{"name": "test", "version": "2.0.0"}')

            # Generate new fingerprint
            fp2 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Should be different (detected change)
            assert fp1.fingerprint != fp2.fingerprint


class TestGitMetadataInFingerprint:
    """Test Git metadata inclusion - AC2."""

    def test_fingerprint_includes_git_metadata(self):
        """Should include git metadata in fingerprint - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            # Include git metadata (FIX HIGH #3: Use CommitInfo objects)
            git_result = GitHistoryResult(
                git_available=True,
                total_commits=100,
                current_branch="main",
                recent_commits=[
                    CommitInfo(
                        message="feat: Add feature",
                        author="Alice",
                        date="2025-12-18T00:00:00Z",
                        hash="abc1234"
                    )
                ],
                contributors=["Alice"],
                commits_per_week=5.0,
                first_commit_date="2023-01-01T00:00:00Z",
                last_commit_date="2025-12-18T00:00:00Z",
                repository_age_days=1052,
                branch_count=3,
                is_actively_maintained=True,
                confidence=0.95,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            # Git metadata hash should not be empty
            assert fingerprint.components.git_metadata_hash != ""
            assert len(fingerprint.components.git_metadata_hash) > 0

    def test_fingerprint_without_git_metadata(self):
        """Should handle non-Git projects gracefully - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            # No git metadata
            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            # Should still generate valid fingerprint
            assert fingerprint is not None
            assert len(fingerprint.fingerprint) >= 16


class TestLanguageFrameworkContext:
    """Test language and framework inclusion - AC3."""

    def test_fingerprint_includes_language_context(self):
        """Should include language information in fingerprint - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.11",
                confidence=0.95,
                markers_found=["requirements.txt"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version="3.11",
                package_manager="pip",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["requirements.txt"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            # Language hash should be included
            assert fingerprint.components.language_version_hash != ""
            assert "python" in fingerprint.components.language_version_hash.lower() or len(
                fingerprint.components.language_version_hash
            ) > 0


class TestCacheValidation:
    """Test cache validation logic - AC6."""

    def test_cache_validation_with_matching_fingerprints(self):
        """Should use cache when fingerprints match - AC6."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))

            # Generate fingerprints
            fp1 = generator.generate_fingerprint(tech_result, files_result, git_result)
            fp2 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Create cache timestamps
            now = datetime.now(timezone.utc)
            cache_timestamp = now - timedelta(hours=1)

            # Validate cache (FIX MEDIUM #7: Updated parameter order to cached, current)
            is_valid = generator.validate_cache(fp2, fp1, cache_timestamp)

            assert is_valid is True

    def test_cache_validation_with_different_fingerprints(self):
        """Should invalidate cache when fingerprints differ - AC6."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fp1 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Modify file to create different fingerprint
            Path(tmpdir, "package.json").write_text('{"name": "test2"}')
            fp2 = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Create cache timestamp
            now = datetime.now(timezone.utc)
            cache_timestamp = now - timedelta(hours=1)

            # Validate cache (FIX MEDIUM #7: Updated parameter order to cached, current)
            is_valid = generator.validate_cache(fp1, fp2, cache_timestamp)

            assert is_valid is False

    def test_cache_validation_with_expired_ttl(self):
        """Should invalidate cache when TTL expired - AC6."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fp = generator.generate_fingerprint(tech_result, files_result, git_result)

            # Create old cache timestamp (25 hours ago, exceeds 24h TTL)
            now = datetime.now(timezone.utc)
            old_cache_timestamp = now - timedelta(hours=25)

            # Validate cache (FIX MEDIUM #7: Parameter order unchanged since both are same fp)
            is_valid = generator.validate_cache(fp, fp, old_cache_timestamp, ttl_hours=24)

            assert is_valid is False


class TestPerformance:
    """Test performance within budget - AC7."""

    def test_fingerprint_generation_within_budget(self):
        """Should complete fingerprint generation within 1 second - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create multiple package files
            Path(tmpdir, "package.json").write_text('{"name": "test"}')
            Path(tmpdir, "requirements.txt").write_text("requests==2.28.0\nnumpy==1.24.0")
            Path(tmpdir, "pyproject.toml").write_text("[project]\nname='test'")

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.PYTHON,
                version="3.11",
                confidence=0.95,
                markers_found=["pyproject.toml", "requirements.txt"],
                secondary_languages=[ProjectLanguage.NODEJS],
            )

            git_result = GitHistoryResult(
                git_available=True,
                total_commits=1000,
                current_branch="main",
                recent_commits=[
                    CommitInfo(
                        message="feat: Add",
                        author="Alice",
                        date="2025-12-18T00:00:00Z",
                        hash="abc1234"
                    )
                ],
                contributors=["Alice"],
                commits_per_week=10.0,
                first_commit_date="2023-01-01T00:00:00Z",
                last_commit_date="2025-12-18T00:00:00Z",
                repository_age_days=1052,
                branch_count=5,
                is_actively_maintained=True,
                confidence=0.95,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.PYTHON,
                dependencies=[],
                dev_dependencies=[],
                target_version="3.11",
                package_manager="pip",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["pyproject.toml", "requirements.txt", "package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))

            start_time = time.perf_counter()
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )
            elapsed = time.perf_counter() - start_time

            assert elapsed < 1.0  # Must complete within 1 second
            assert fingerprint is not None


class TestFingerprintFormat:
    """Test fingerprint format and consistency - AC8."""

    def test_fingerprint_hexadecimal_format(self):
        """Fingerprint should be hexadecimal string - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            # Should be hexadecimal
            assert all(c in "0123456789abcdef" for c in fingerprint.fingerprint)
            # Should be 40+ characters
            assert len(fingerprint.fingerprint) >= 40

    def test_fingerprint_includes_version(self):
        """Fingerprint should include version field - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "package.json").write_text('{"name": "test"}')

            tech_result = ProjectTypeDetectionResult(
                primary_language=ProjectLanguage.NODEJS,
                version="18.0.0",
                confidence=0.95,
                markers_found=["package.json"],
                secondary_languages=[],
            )

            git_result = GitHistoryResult(
                git_available=False,
                total_commits=None,
                current_branch=None,
                recent_commits=[],
                contributors=[],
                commits_per_week=None,
                first_commit_date=None,
                last_commit_date=None,
                repository_age_days=None,
                branch_count=None,
                is_actively_maintained=False,
                confidence=0.0,
            )

            metadata = ProjectMetadata(
                name="test",
                version="1.0.0",
                source_language=ProjectLanguage.NODEJS,
                dependencies=[],
                dev_dependencies=[],
                target_version="18.0.0",
                package_manager="npm",
            )

            files_result = ProjectIndicatorResult(
                metadata=metadata,
                files_found=["package.json"],
                lock_files_present=set(),
                confidence=0.95,
            )

            generator = FingerprintGenerator(Path(tmpdir))
            fingerprint = generator.generate_fingerprint(
                tech_result, files_result, git_result
            )

            assert fingerprint.version == 1
            assert fingerprint.algorithm == "sha256"
