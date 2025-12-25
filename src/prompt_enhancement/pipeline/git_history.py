"""
Git History Analyzer - Extract Git metadata for development pattern analysis.

This module implements Story 2.3: Extract Git History and Project Context.
Analyzes Git repositories to extract commit history, contributors, and development patterns.

Safe execution with graceful degradation for non-Git projects or permission-denied scenarios.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Optional

from .tech_stack import ProjectLanguage
from ..cli.performance import PerformanceTracker  # FIX #7: Integrate PerformanceTracker


logger = logging.getLogger(__name__)


# ============================================================================
# Data Structures
# ============================================================================


@dataclass
class ContributorInfo:
    """Information about a project contributor."""

    name: str
    commit_count: int
    percentage: float


@dataclass
class CommitInfo:
    """Information about a single commit (FIX #4: AC2 - structured commit data)."""

    message: str
    author: str
    date: str
    hash: str


@dataclass
class GitHistoryResult:
    """Complete Git history analysis result."""

    git_available: bool
    total_commits: Optional[int]
    current_branch: Optional[str]
    recent_commits: List[CommitInfo]  # FIX #4: Changed from List[str] to List[CommitInfo]
    contributors: List[str]
    commits_per_week: Optional[float]
    first_commit_date: Optional[str]
    last_commit_date: Optional[str]
    repository_age_days: Optional[int]
    branch_count: Optional[int]
    is_actively_maintained: bool
    confidence: float
    branch_structure: Optional[dict] = None  # FIX #5: Add branch structure analysis


# ============================================================================
# GitHistoryDetector Class
# ============================================================================


class GitHistoryDetector:
    """
    Detects and analyzes Git history from a project repository.

    Extracts commit history, contributors, and development patterns.
    Gracefully handles non-Git projects and permission errors.

    Attributes:
        project_root: Root directory of the project
        detected_language: Language detected from Story 2.1 (optional context)
        max_commits: Maximum commits to read (default 100)
        timeout_sec: Timeout for Git operations (default 2.0)
    """

    # Default configuration
    DEFAULT_MAX_COMMITS = 100
    DEFAULT_TIMEOUT_SEC = 2.0
    RECENT_COMMITS_LIMIT = 10
    ACTIVE_MAINTENANCE_DAYS = 30
    TOP_CONTRIBUTORS_LIMIT = 5

    def __init__(
        self,
        project_root: Path,
        detected_language: Optional[ProjectLanguage] = None,
        max_commits: int = DEFAULT_MAX_COMMITS,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
        performance_tracker: Optional[PerformanceTracker] = None,  # FIX #7
    ):
        """
        Initialize Git history detector.

        Args:
            project_root: Root directory to analyze
            detected_language: Language from Story 2.1 (optional)
            max_commits: Max commits to process (default 100)
            timeout_sec: Timeout for Git commands (default 2.0 seconds)
            performance_tracker: PerformanceTracker from Story 1.4 (optional, FIX #7)
        """
        self.project_root = Path(project_root)
        self.detected_language = detected_language
        self.max_commits = max_commits
        self.timeout_sec = timeout_sec
        self.start_time = time.perf_counter()
        self.performance_tracker = performance_tracker  # FIX #7

    # ========================================================================
    # Main Entry Point
    # ========================================================================

    def extract_git_history(self) -> Optional[GitHistoryResult]:
        """
        Extract Git history and return analysis result.

        FIX #7: Integrated with PerformanceTracker for phase tracking.

        Returns:
            GitHistoryResult with all analysis data, or None on critical failure
        """
        try:
            # FIX #7: Start performance tracking
            if self.performance_tracker:
                self.performance_tracker.start_phase("git_history")

            # Check if Git is available
            if not self._check_git_available():
                logger.debug(f"Git not available in {self.project_root}")
                return GitHistoryResult(
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

            # Check timeout
            if self._is_timeout():
                logger.warning("Git history analysis timeout - stopping")
                return None

            # Get basic info
            total_commits = self._get_total_commit_count()
            current_branch = self._get_current_branch()

            # Get commit log
            log_output = self._get_recent_log()

            # Parse results
            recent_commits = self._parse_recent_commits(log_output)
            contributors = self._parse_contributors(log_output)
            stats = self._calculate_statistics(log_output, total_commits)

            # Get branch info
            branch_count = self._get_branch_count()
            # FIX #5: Add branch structure analysis
            branch_structure = self._analyze_branch_structure()

            # Calculate confidence
            confidence = self._calculate_confidence(
                total_commits is not None,
                len(recent_commits) > 0,
                len(contributors) > 0,
                stats.get("repository_age_days") is not None,
            )

            result = GitHistoryResult(
                git_available=True,
                total_commits=total_commits,
                current_branch=current_branch,
                recent_commits=recent_commits,
                contributors=contributors,
                commits_per_week=stats.get("commits_per_week"),
                first_commit_date=stats.get("first_commit_date"),
                last_commit_date=stats.get("last_commit_date"),
                repository_age_days=stats.get("repository_age_days"),
                branch_count=branch_count,
                is_actively_maintained=stats.get("is_actively_maintained", False),
                confidence=confidence,
                branch_structure=branch_structure,  # FIX #5
            )

            # FIX #7: End performance tracking
            if self.performance_tracker:
                self.performance_tracker.end_phase("git_history")

            return result

        except Exception as e:
            logger.error(f"Error extracting git history: {e}", exc_info=True)
            # FIX #7: End performance tracking on error too
            if self.performance_tracker:
                self.performance_tracker.end_phase("git_history")
            return None

    # ========================================================================
    # Git Availability Detection
    # ========================================================================

    def _check_git_available(self) -> bool:
        """
        Check if Git repository exists and is readable.

        Returns:
            True if .git exists and is accessible
        """
        git_dir = self.project_root / ".git"
        if not git_dir.exists():
            return False

        try:
            # Test if git commands work
            result = self._run_git_command(
                ["git", "rev-parse", "--is-inside-work-tree"],
                timeout_sec=1.0,
            )
            return result is not None
        except Exception as e:
            logger.debug(f"Git availability check failed: {e}")
            return False

    # ========================================================================
    # Git Command Execution
    # ========================================================================

    def _run_git_command(
        self,
        command: List[str],
        timeout_sec: Optional[float] = None,
    ) -> Optional[str]:
        """
        Execute Git command safely with timeout.

        Args:
            command: Git command as list (e.g., ['git', 'log', ...])
            timeout_sec: Timeout in seconds (uses self.timeout_sec if not specified)

        Returns:
            Command output as string, or None if error/timeout
        """
        if timeout_sec is None:
            timeout_sec = self.timeout_sec

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout_sec,
                cwd=str(self.project_root),
            )
            if result.returncode == 0:
                return result.stdout.strip()
            logger.debug(f"Git command failed: {' '.join(command)}")
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

    # ========================================================================
    # Git Data Retrieval
    # ========================================================================

    def _get_total_commit_count(self) -> Optional[int]:
        """Get total commit count."""
        output = self._run_git_command(["git", "rev-list", "--all", "--count"])
        if output:
            try:
                return int(output)
            except ValueError:
                pass
        return None

    def _get_current_branch(self) -> Optional[str]:
        """Get current branch name."""
        output = self._run_git_command(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        return output if output else None

    def _get_recent_log(self) -> str:
        """Get recent commit log in structured format."""
        output = self._run_git_command(
            [
                "git",
                "log",
                f"--max-count={self.max_commits}",
                "--format=%h|%an|%ai|%s",
                "--all",
            ]
        )
        return output if output else ""

    def _get_branch_count(self) -> Optional[int]:
        """Get number of branches."""
        output = self._run_git_command(["git", "branch", "-a", "--format=%(refname)"])
        if output:
            # Count non-empty lines (each is a branch)
            return len([line for line in output.split("\n") if line.strip()])
        return None

    def _analyze_branch_structure(self) -> Optional[dict]:
        """
        Analyze branch structure and naming patterns (FIX #5: AC3).

        Returns:
            Dictionary with branch structure analysis:
            - main_branch: Main branch name
            - total_branches: Total count
            - feature_branches: Count of feature/* branches
            - bugfix_branches: Count of bugfix/* or fix/* branches
            - release_branches: Count of release/* branches
            - other_branches: Count of other branches
        """
        output = self._run_git_command(["git", "branch", "-a", "--format=%(refname)"])
        if not output:
            return None

        structure = {
            "main_branch": self._get_current_branch(),
            "total_branches": 0,
            "feature_branches": 0,
            "bugfix_branches": 0,
            "release_branches": 0,
            "hotfix_branches": 0,
            "other_branches": 0,
        }

        for line in output.split("\n"):
            if not line.strip():
                continue

            structure["total_branches"] += 1
            branch_name = line.strip().lower()

            # Analyze naming patterns
            if "feature/" in branch_name or "/feature/" in branch_name:
                structure["feature_branches"] += 1
            elif "bugfix/" in branch_name or "fix/" in branch_name or "/bugfix/" in branch_name:
                structure["bugfix_branches"] += 1
            elif "release/" in branch_name or "/release/" in branch_name:
                structure["release_branches"] += 1
            elif "hotfix/" in branch_name or "/hotfix/" in branch_name:
                structure["hotfix_branches"] += 1
            else:
                structure["other_branches"] += 1

        return structure

    # ========================================================================
    # Commit Message Parsing
    # ========================================================================

    def _parse_recent_commits(self, log_output: str) -> List[CommitInfo]:
        """
        Extract recent commit information from git log output.

        FIX #4: Returns structured CommitInfo objects with author, date, message.

        Expected format: 'hash|author|date|message'
        Limits to RECENT_COMMITS_LIMIT (10) most recent commits.

        Args:
            log_output: Output from git log command

        Returns:
            List of CommitInfo objects
        """
        commits = []
        if not log_output:
            return commits

        for line in log_output.split("\n")[: self.RECENT_COMMITS_LIMIT]:
            if not line.strip():
                continue

            try:
                parts = line.split("|")
                if len(parts) >= 4:
                    # Extract fields
                    hash_short = parts[0][:7]
                    author = parts[1]
                    # Remove email if present (AC2: name only, not email)
                    if "<" in author:
                        author = author.split("<")[0].strip()
                    date = parts[2]
                    message = parts[3]

                    # Clean message: take first line, limit length
                    message_clean = message.split("\n")[0][:100]

                    # Skip merge commits with generic messages
                    if message.startswith("Merge ") and len(message) < 30:
                        continue

                    commits.append(CommitInfo(
                        message=message_clean,
                        author=author,
                        date=date,
                        hash=hash_short
                    ))
            except Exception as e:
                logger.debug(f"Error parsing commit line: {e}")
                continue

        return commits

    # ========================================================================
    # Contributor Analysis
    # ========================================================================

    def _parse_contributors(self, log_output: str) -> List[str]:
        """
        Extract contributor names from git log.

        FIX #2: git shortlog does NOT accept --max-count flag, removed.
        FIX #3: Added explicit top-5 limit in Python.

        Args:
            log_output: Output from git log command

        Returns:
            List of top contributor names (limited to TOP_CONTRIBUTORS_LIMIT)
        """
        # Use git shortlog to get contributors efficiently
        # NOTE: shortlog doesn't support --max-count, we limit in Python instead
        shortlog_output = self._run_git_command(
            ["git", "shortlog", "-sn", "--all"]
        )

        contributors = []
        if shortlog_output:
            for line in shortlog_output.split("\n"):
                if not line.strip():
                    continue

                try:
                    # Format: 'count  name'
                    parts = line.strip().split(maxsplit=1)
                    if len(parts) == 2 and parts[0].isdigit():
                        name = parts[1]
                        # Remove email if present
                        if "<" in name:
                            name = name.split("<")[0].strip()
                        contributors.append(name)
                except Exception as e:
                    logger.debug(f"Error parsing contributor line: {e}")
                    continue

        # FIX #3: Limit to top 5 contributors
        return contributors[:self.TOP_CONTRIBUTORS_LIMIT]

    # ========================================================================
    # Statistics Calculation
    # ========================================================================

    def _calculate_statistics(
        self,
        log_output: str,
        total_commits: Optional[int],
    ) -> dict:
        """
        Calculate development statistics from git log output.

        Args:
            log_output: Output from git log command
            total_commits: Total commit count

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_commits": total_commits or 0,
            "first_commit_date": None,
            "last_commit_date": None,
            "commits_per_week": None,
            "repository_age_days": None,
            "is_actively_maintained": False,
        }

        if not log_output:
            return stats

        try:
            lines = log_output.strip().split("\n")
            all_dates = []

            # Parse all dates from log output
            for line in lines:
                try:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        date_str = parts[2].strip()
                        # Parse format: '2025-12-18 10:30:45 +0000'
                        # Convert to ISO format with proper timezone
                        try:
                            # Split date/time from timezone
                            if " " in date_str:
                                datetime_part, tz_part = date_str.rsplit(" ", 1)
                                # Parse datetime
                                dt = datetime.strptime(datetime_part, "%Y-%m-%d %H:%M:%S")
                                # Handle timezone (+0000 or -0500 etc.)
                                if tz_part.startswith(("+", "-")):
                                    tz_hours = int(tz_part[1:3])
                                    tz_mins = int(tz_part[3:5])
                                    tz_offset = timedelta(hours=tz_hours, minutes=tz_mins)
                                    if tz_part.startswith("-"):
                                        tz_offset = -tz_offset
                                    # Make timezone-aware
                                    tz = timezone(tz_offset)
                                    date_obj = dt.replace(tzinfo=tz)
                                else:
                                    # Assume UTC if no timezone
                                    date_obj = dt.replace(tzinfo=timezone.utc)
                            else:
                                # Fallback: parse as UTC
                                date_obj = datetime.fromisoformat(date_str).replace(tzinfo=timezone.utc)
                            all_dates.append(date_obj)
                        except (ValueError, IndexError):
                            # Skip malformed dates
                            pass
                except Exception:
                    continue

            if all_dates:
                # Sort dates
                all_dates.sort()

                # First and last dates
                stats["first_commit_date"] = all_dates[0].isoformat()
                stats["last_commit_date"] = all_dates[-1].isoformat()

                # Repository age
                age_days = (all_dates[-1] - all_dates[0]).days
                stats["repository_age_days"] = max(age_days, 0)

                # Commits per week
                weeks = max(age_days / 7, 0.1)  # Avoid division by zero
                commits = total_commits or len(all_dates)
                stats["commits_per_week"] = commits / weeks

                # Check if actively maintained
                now = datetime.now(timezone.utc)
                last_commit_date = all_dates[-1]
                # Ensure both are timezone-aware for comparison
                if last_commit_date.tzinfo is None:
                    last_commit_date = last_commit_date.replace(tzinfo=timezone.utc)

                days_since_last = (now - last_commit_date).days
                stats["is_actively_maintained"] = days_since_last < self.ACTIVE_MAINTENANCE_DAYS

        except Exception as e:
            logger.debug(f"Error calculating statistics: {e}")

        return stats

    # ========================================================================
    # Confidence Scoring
    # ========================================================================

    def _calculate_confidence(
        self,
        has_total_commits: bool,
        has_recent_commits: bool,
        has_contributors: bool,
        has_dates: bool,
    ) -> float:
        """
        Calculate confidence score based on available data.

        Args:
            has_total_commits: Whether total_commits was extracted
            has_recent_commits: Whether recent commits were found
            has_contributors: Whether contributors were identified
            has_dates: Whether date information is available

        Returns:
            Confidence score 0.0-1.0
        """
        score = 0.0

        # Each factor worth 0.25
        if has_total_commits:
            score += 0.25
        if has_recent_commits:
            score += 0.25
        if has_contributors:
            score += 0.25
        if has_dates:
            score += 0.25

        return min(score, 1.0)

    # ========================================================================
    # Timeout Management
    # ========================================================================

    def _is_timeout(self) -> bool:
        """
        Check if timeout has been exceeded (FIX #7: Use PerformanceTracker if available).

        Returns:
            True if timeout exceeded
        """
        if self.performance_tracker:
            # Use PerformanceTracker's timeout checking
            return self.performance_tracker.check_soft_timeout(self.timeout_sec)
        else:
            # Fallback to manual tracking
            elapsed = time.perf_counter() - self.start_time
            return elapsed > self.timeout_sec
