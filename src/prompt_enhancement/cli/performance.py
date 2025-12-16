"""
Performance tracking and optimization.
Handles time budgeting, caching, timeout management, and performance metrics.
"""

import time
import hashlib
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, Optional, Any

# Configure logging
logger = logging.getLogger(__name__)


class ProjectFingerprint:
    """Generate and manage project fingerprints for caching."""

    # Default marker files to include in fingerprint
    MARKER_FILES = [
        "package.json",
        "pyproject.toml",
        "requirements.txt",
        "go.mod",
        "Cargo.toml",
        "pom.xml",
        ".git",
    ]

    @staticmethod
    def compute_fingerprint(directory: str = ".") -> str:
        """
        Compute project fingerprint from marker files.

        Args:
            directory: Project directory path

        Returns:
            Hexadecimal fingerprint string
        """
        hash_obj = hashlib.md5()

        # Hash the existence and content of marker files
        for marker in ProjectFingerprint.MARKER_FILES:
            marker_path = os.path.join(directory, marker)

            if os.path.exists(marker_path):
                if os.path.isfile(marker_path):
                    try:
                        with open(marker_path, "rb") as f:
                            content = f.read(1024)  # Read first 1KB
                            hash_obj.update(content)
                    except (IOError, OSError):
                        pass
                else:
                    # Directory exists, just hash its path
                    hash_obj.update(marker.encode("utf-8"))

        fingerprint = hash_obj.hexdigest()

        logger.debug(f"Computed project fingerprint: {fingerprint}")

        return fingerprint


@dataclass
class TimeBudget:
    """Time budget allocation for phases."""
    total_seconds: float
    analysis_seconds: float
    standards_seconds: float
    llm_seconds: float
    formatting_seconds: float
    cache_seconds: float

    def get_remaining_time(self) -> float:
        """
        Get remaining time buffer.

        Returns:
            Remaining buffer in seconds
        """
        allocated = (
            self.analysis_seconds
            + self.standards_seconds
            + self.llm_seconds
            + self.formatting_seconds
            + self.cache_seconds
        )
        return self.total_seconds - allocated


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""
    total_execution_time: float
    phase_times: Dict[str, float] = field(default_factory=dict)
    cache_hit: bool = False
    cache_age_seconds: Optional[float] = None
    quality_level: str = "full"


class PerformanceTracker:
    """Tracks performance metrics and enforces time budgets."""

    # Performance constants
    SOFT_TIMEOUT_SECONDS = 15
    HARD_TIMEOUT_SECONDS = 60
    CACHE_DEFAULT_TTL_SECONDS = 3600  # 1 hour

    def __init__(self):
        """Initialize the performance tracker."""
        self.start_time = time.perf_counter()
        self.phase_times: Dict[str, float] = {}
        self.phase_start_times: Dict[str, float] = {}
        self.budget: Optional[TimeBudget] = None
        self.cache: Dict[str, tuple] = {}  # (value, expiry_time)
        self.cache_hit_flag = False
        self.cache_age_seconds: Optional[float] = None

        logger.debug("PerformanceTracker initialized")

    def set_budget(self, budget: TimeBudget) -> None:
        """Set time budget for phases."""
        self.budget = budget
        logger.debug(f"Time budget set: {budget.total_seconds}s total")

    def start_phase(self, phase_name: str) -> None:
        """
        Start tracking a phase.

        Args:
            phase_name: Name of the phase
        """
        self.phase_start_times[phase_name] = time.perf_counter()
        logger.debug(f"Phase started: {phase_name}")

    def end_phase(self, phase_name: str) -> None:
        """
        End tracking a phase and record duration.

        Args:
            phase_name: Name of the phase
        """
        if phase_name in self.phase_start_times:
            elapsed = time.perf_counter() - self.phase_start_times[phase_name]
            self.phase_times[phase_name] = elapsed
            logger.debug(f"Phase ended: {phase_name} ({elapsed:.3f}s)")

    def get_time_remaining(self, total_seconds: float) -> float:
        """
        Get time remaining from start.

        Args:
            total_seconds: Total time budget

        Returns:
            Remaining time in seconds
        """
        elapsed = time.perf_counter() - self.start_time
        remaining = total_seconds - elapsed
        return remaining

    def check_soft_timeout(self, soft_timeout_seconds: float = SOFT_TIMEOUT_SECONDS) -> bool:
        """
        Check if soft timeout (performance target) exceeded.

        Args:
            soft_timeout_seconds: Soft timeout duration

        Returns:
            True if soft timeout exceeded
        """
        elapsed = time.perf_counter() - self.start_time
        exceeded = elapsed > soft_timeout_seconds
        if exceeded:
            logger.warning(f"Soft timeout exceeded: {elapsed:.1f}s > {soft_timeout_seconds}s")
        return exceeded

    def check_hard_timeout(self, hard_timeout_seconds: float = HARD_TIMEOUT_SECONDS) -> bool:
        """
        Check if hard timeout (Claude Code limit) exceeded.

        Args:
            hard_timeout_seconds: Hard timeout duration

        Returns:
            True if hard timeout exceeded
        """
        elapsed = time.perf_counter() - self.start_time
        exceeded = elapsed > hard_timeout_seconds
        if exceeded:
            logger.error(f"Hard timeout exceeded: {elapsed:.1f}s > {hard_timeout_seconds}s")
        return exceeded

    def is_over_budget(self, phase_budget_seconds: float, elapsed_seconds: float) -> bool:
        """
        Check if phase is over budget.

        Args:
            phase_budget_seconds: Budget for this phase
            elapsed_seconds: Time already elapsed

        Returns:
            True if over budget
        """
        over = elapsed_seconds > phase_budget_seconds
        if over:
            logger.warning(f"Phase over budget: {elapsed_seconds:.1f}s > {phase_budget_seconds}s")
        return over

    def set_cache(
        self,
        key: str,
        value: Any,
        ttl_seconds: float = CACHE_DEFAULT_TTL_SECONDS
    ) -> None:
        """
        Store value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
        """
        expiry_time = time.perf_counter() + ttl_seconds
        self.cache[key] = (value, expiry_time)
        logger.debug(f"Cached: {key} (TTL: {ttl_seconds}s)")

    def get_cache(self, key: str) -> Optional[Any]:
        """
        Retrieve value from cache if not expired.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        if key not in self.cache:
            logger.debug(f"Cache miss: {key}")
            return None

        value, expiry_time = self.cache[key]

        # Check if expired
        if time.perf_counter() > expiry_time:
            del self.cache[key]
            logger.debug(f"Cache expired: {key}")
            return None

        logger.debug(f"Cache hit: {key}")
        return value

    def record_cache_hit(self, cache_age_seconds: float) -> None:
        """
        Record a cache hit.

        Args:
            cache_age_seconds: Age of cache entry in seconds
        """
        self.cache_hit_flag = True
        self.cache_age_seconds = cache_age_seconds
        logger.info(f"Cache hit recorded (age: {cache_age_seconds}s)")

    def record_cache_miss(self) -> None:
        """Record a cache miss."""
        self.cache_hit_flag = False
        self.cache_age_seconds = None
        logger.info("Cache miss recorded")

    def get_metrics(self) -> PerformanceMetrics:
        """
        Get current performance metrics.

        Returns:
            PerformanceMetrics snapshot
        """
        total_time = time.perf_counter() - self.start_time

        # Determine quality level
        quality_level = "full"
        if total_time > self.SOFT_TIMEOUT_SECONDS:
            quality_level = "degraded"

        metrics = PerformanceMetrics(
            total_execution_time=total_time,
            phase_times=self.phase_times.copy(),
            cache_hit=self.cache_hit_flag,
            cache_age_seconds=self.cache_age_seconds,
            quality_level=quality_level
        )

        logger.info(
            f"Metrics snapshot: {total_time:.3f}s total, "
            f"{len(self.phase_times)} phases, "
            f"cache_hit={self.cache_hit_flag}, "
            f"quality={quality_level}"
        )

        return metrics

    def get_summary(self) -> str:
        """
        Get human-readable performance summary.

        Returns:
            Formatted summary string
        """
        metrics = self.get_metrics()

        lines = [
            "⏱️ Performance Summary:",
            f"   Total: {metrics.total_execution_time:.2f}s",
        ]

        # Phase breakdown
        if metrics.phase_times:
            lines.append("   Phases:")
            for phase_name, duration in metrics.phase_times.items():
                lines.append(f"     • {phase_name}: {duration:.2f}s")

        # Cache status
        if metrics.cache_hit:
            lines.append(f"   ⚡ Cache hit (age: {metrics.cache_age_seconds}s)")
        else:
            lines.append("   📊 Full analysis (cache miss)")

        # Quality level
        if metrics.quality_level != "full":
            lines.append(f"   ⚠️ Quality: {metrics.quality_level}")

        return "\n".join(lines)
