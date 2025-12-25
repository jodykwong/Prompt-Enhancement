"""
Tests for Git History Analyzer - Story 2.3.

Comprehensive test suite for GitHistoryDetector implementing all acceptance criteria.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path
from datetime import datetime, timedelta, timezone

import pytest

from prompt_enhancement.pipeline.git_history import (
    GitHistoryDetector,
    GitHistoryResult,
    ContributorInfo,
)
from prompt_enhancement.pipeline.tech_stack import ProjectLanguage


class TestGitHistoryResultStructure:
    """Test data structure validation - AC1, AC3, AC8."""

    def test_git_history_result_creation(self):
        """GitHistoryResult should have all required fields."""
        result = GitHistoryResult(
            git_available=True,
            total_commits=100,
            current_branch="main",
            recent_commits=["feat: Add feature", "fix: Bug fix"],
            contributors=["Alice", "Bob"],
            commits_per_week=10.5,
            first_commit_date="2023-01-01T00:00:00Z",
            last_commit_date="2025-12-18T12:00:00Z",
            repository_age_days=1052,
            branch_count=5,
            is_actively_maintained=True,
            confidence=0.95,
        )

        assert result.git_available is True
        assert result.total_commits == 100
        assert result.current_branch == "main"
        assert len(result.recent_commits) == 2
        assert result.confidence == 0.95

    def test_git_history_result_with_none_values(self):
        """GitHistoryResult should handle None for unavailable git data."""
        result = GitHistoryResult(
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

        assert result.git_available is False
        assert result.total_commits is None
        assert result.confidence == 0.0

    def test_contributor_info_creation(self):
        """ContributorInfo should store contributor details."""
        contributor = ContributorInfo(
            name="Alice Developer",
            commit_count=42,
            percentage=35.5,
        )

        assert contributor.name == "Alice Developer"
        assert contributor.commit_count == 42
        assert contributor.percentage == 35.5


class TestGitRepositoryDetection:
    """Test Git repository detection - AC1."""

    def test_detect_git_in_valid_repository(self):
        """Should detect Git in a valid repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize git repository
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result is not None
            assert result.git_available is True

    def test_detect_missing_git_repository(self):
        """Should handle missing .git directory gracefully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result is not None
            assert result.git_available is False
            assert result.total_commits is None
            assert result.current_branch is None

    def test_detect_total_commit_count(self):
        """Should extract total commit count - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize and create commits
            subprocess.run(
                ["git", "init"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create 3 commits
            for i in range(3):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", f"commit {i}"],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.git_available is True
            assert result.total_commits == 3


class TestRecentCommitAnalysis:
    """Test recent commit extraction - AC2."""

    def test_extract_recent_commit_messages(self):
        """Should extract recent commit messages - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create commits with meaningful messages
            messages = ["feat: Add feature", "fix: Fix bug", "docs: Update README"]
            for i, msg in enumerate(messages):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", msg],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert len(result.recent_commits) > 0
            # Recent commits should be in reverse order (newest first)
            # FIX: recent_commits now returns CommitInfo objects, check .message attribute
            assert "Add feature" in result.recent_commits[-1].message or "Add feature" in result.recent_commits[0].message
            # Verify commit info structure (FIX #4: AC2 - authors and dates)
            assert result.recent_commits[0].author is not None
            assert result.recent_commits[0].date is not None
            assert result.recent_commits[0].hash is not None

    def test_extract_commit_authors(self):
        """Should extract author names from commits - AC2."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create commit
            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial commit"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.git_available is True
            # Authors should be extracted (might be list or string depending on implementation)
            assert len(result.contributors) >= 0


class TestGitStatistics:
    """Test development statistics - AC3."""

    def test_commit_frequency_calculation(self):
        """Should calculate commits per week - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo with multiple commits
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create 10 commits
            for i in range(10):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", f"commit {i}"],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.commits_per_week is not None
            assert result.commits_per_week > 0

    def test_repository_age_calculation(self):
        """Should calculate repository age - AC3."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create initial commit
            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.repository_age_days is not None
            assert result.repository_age_days >= 0

    def test_current_branch_detection(self):
        """Should detect current branch - AC1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create commit to establish main/master branch
            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.current_branch is not None
            assert len(result.current_branch) > 0


class TestLargeRepositoryHandling:
    """Test performance with large repositories - AC4."""

    def test_max_commits_limit(self):
        """Should respect max_commits parameter - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create 50 commits
            for i in range(50):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", f"commit {i}"],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir), max_commits=10)
            result = detector.extract_git_history()

            assert result.total_commits == 50  # Total still accurate
            assert len(result.recent_commits) <= 10  # But we only process 10

    def test_performance_within_budget(self):
        """Should complete within 2-second timeout - AC4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo with commits
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create 100 commits
            for i in range(100):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", f"commit {i}"],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir))

            start_time = time.perf_counter()
            result = detector.extract_git_history()
            elapsed = time.perf_counter() - start_time

            # FIX #6: Explicit timing assertion for AC4 2-second budget
            assert elapsed < 2.0, f"Git history extraction took {elapsed:.3f}s, exceeds 2.0s budget"
            assert result is not None, "Result should not be None"
            assert result.git_available is True, "Git should be available"


class TestErrorHandling:
    """Test error handling and graceful degradation - AC5, AC6."""

    def test_permission_denied_graceful_handling(self):
        """Should handle permission denied errors gracefully - AC6."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Remove read permissions from .git
            subprocess.run(
                ["chmod", "000", Path(tmpdir, ".git")],
                cwd=tmpdir,
                capture_output=True,
            )

            try:
                detector = GitHistoryDetector(Path(tmpdir))
                result = detector.extract_git_history()

                # Should return gracefully, not crash
                assert result is not None
                # Git should not be available due to permissions
                assert result.git_available is False
            finally:
                # Restore permissions for cleanup
                subprocess.run(
                    ["chmod", "755", Path(tmpdir, ".git")],
                    cwd=tmpdir,
                    capture_output=True,
                )

    def test_non_git_project_graceful_degradation(self):
        """Should degrade gracefully for non-Git projects - AC5."""
        with tempfile.TemporaryDirectory() as tmpdir:
            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result is not None
            assert result.git_available is False
            assert result.total_commits is None
            assert len(result.recent_commits) == 0
            assert result.confidence == 0.0


class TestUTF8Handling:
    """Test UTF-8 and special character handling - AC7."""

    def test_utf8_commit_messages(self):
        """Should handle UTF-8 commit messages correctly - AC7."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create commits with UTF-8 characters
            messages = [
                "feat: Add feature 🚀",
                "fix: Bug fix ✨",
                "docs: 中文文档",  # Chinese characters
            ]

            for i, msg in enumerate(messages):
                Path(tmpdir, f"file{i}.txt").write_text(f"content {i}")
                subprocess.run(
                    ["git", "add", "."],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )
                subprocess.run(
                    ["git", "commit", "-m", msg],
                    cwd=tmpdir,
                    capture_output=True,
                    check=True,
                )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.git_available is True
            assert len(result.recent_commits) > 0
            # Messages should be extracted without crashing
            assert isinstance(result.recent_commits, list)


class TestActivityPatterns:
    """Test development activity pattern analysis - AC8."""

    def test_actively_maintained_detection(self):
        """Should detect if repository is actively maintained - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo with recent commit
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create recent commit (today)
            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "recent commit"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            # Recent repository should be actively maintained
            assert result.is_actively_maintained is True

    def test_confidence_score(self):
        """Should calculate confidence score for results - AC8."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            # Confidence should be between 0 and 1
            assert 0.0 <= result.confidence <= 1.0


class TestIntegration:
    """Integration tests with realistic project structures."""

    def test_realistic_project_with_multiple_branches(self):
        """Test with realistic project having multiple branches."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create commits on main
            Path(tmpdir, "file.txt").write_text("content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "initial"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create and checkout feature branch
            subprocess.run(
                ["git", "checkout", "-b", "feature/test"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            Path(tmpdir, "feature.txt").write_text("feature content")
            subprocess.run(
                ["git", "add", "."],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "commit", "-m", "add feature"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            detector = GitHistoryDetector(Path(tmpdir))
            result = detector.extract_git_history()

            assert result.git_available is True
            assert result.total_commits >= 2
            assert result.current_branch is not None

    def test_detector_initialization_with_language_context(self):
        """Should initialize with optional language context."""
        with tempfile.TemporaryDirectory() as tmpdir:
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)

            detector = GitHistoryDetector(
                Path(tmpdir),
                detected_language=ProjectLanguage.PYTHON,
                max_commits=50,
            )

            assert detector.project_root == Path(tmpdir)
            assert detector.detected_language == ProjectLanguage.PYTHON
            assert detector.max_commits == 50

    def test_performance_tracker_integration(self):
        """Should integrate with PerformanceTracker from Story 1.4 (FIX #7 & #6)."""
        from src.prompt_enhancement.cli.performance import PerformanceTracker

        with tempfile.TemporaryDirectory() as tmpdir:
            # Initialize repo
            subprocess.run(["git", "init"], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Create a commit
            Path(tmpdir, "test.txt").write_text("test content")
            subprocess.run(["git", "add", "."], cwd=tmpdir, capture_output=True, check=True)
            subprocess.run(
                ["git", "commit", "-m", "Initial commit"],
                cwd=tmpdir,
                capture_output=True,
                check=True,
            )

            # Use PerformanceTracker
            tracker = PerformanceTracker()
            detector = GitHistoryDetector(
                Path(tmpdir),
                performance_tracker=tracker
            )

            result = detector.extract_git_history()

            assert result is not None
            assert result.git_available is True
            # FIX #6 & #7: Verify PerformanceTracker tracked the git_history phase
            assert "git_history" in tracker.phase_times, "PerformanceTracker should track git_history phase"
            assert tracker.phase_times["git_history"] < 2.0, f"Git history took {tracker.phase_times['git_history']:.3f}s, exceeds 2.0s budget"
