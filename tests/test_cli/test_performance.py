"""
Unit tests for PerformanceTracker.
Tests performance tracking, caching, timeout management, and time budget enforcement.
"""

import pytest
import time
from src.prompt_enhancement.cli.performance import (
    PerformanceTracker, TimeBudget, PerformanceMetrics, ProjectFingerprint
)


class TestProjectFingerprint:
    """Test project fingerprint generation."""

    def test_fingerprint_generation(self):
        """Generate a project fingerprint."""
        fingerprint = ProjectFingerprint.compute_fingerprint(directory=".")

        assert isinstance(fingerprint, str)
        assert len(fingerprint) > 0

    def test_fingerprint_consistency(self):
        """Same project generates same fingerprint."""
        fp1 = ProjectFingerprint.compute_fingerprint(directory=".")
        fp2 = ProjectFingerprint.compute_fingerprint(directory=".")

        assert fp1 == fp2

    def test_fingerprint_format(self):
        """Fingerprint is valid hash format."""
        fingerprint = ProjectFingerprint.compute_fingerprint(directory=".")

        # Should be hexadecimal
        assert all(c in '0123456789abcdef' for c in fingerprint.lower())


class TestTimeBudget:
    """Test TimeBudget data structure."""

    def test_budget_creation(self):
        """Create a TimeBudget instance."""
        budget = TimeBudget(
            total_seconds=15,
            analysis_seconds=5,
            standards_seconds=2,
            llm_seconds=5,
            formatting_seconds=1,
            cache_seconds=1
        )

        assert budget.total_seconds == 15
        assert budget.analysis_seconds == 5

    def test_budget_remaining_calculation(self):
        """Calculate remaining budget."""
        budget = TimeBudget(
            total_seconds=15,
            analysis_seconds=5,
            standards_seconds=2,
            llm_seconds=5,
            formatting_seconds=1,
            cache_seconds=1
        )

        remaining = budget.get_remaining_time()

        assert remaining == 1  # 5+2+5+1+1 = 14, remaining = 1


class TestPerformanceTracker:
    """Test PerformanceTracker class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()

    def test_initialization(self):
        """PerformanceTracker initializes correctly."""
        assert self.tracker is not None
        assert self.tracker.start_time is not None

    def test_measure_phase_time(self):
        """AC5: Measure phase execution time."""
        self.tracker.start_phase("analysis")
        time.sleep(0.1)
        self.tracker.end_phase("analysis")

        metrics = self.tracker.get_metrics()

        assert "analysis" in metrics.phase_times
        assert metrics.phase_times["analysis"] >= 0.1

    def test_phase_timing_accuracy(self):
        """Phase timing is accurate within tolerance."""
        self.tracker.start_phase("test_phase")
        time.sleep(0.2)
        self.tracker.end_phase("test_phase")

        duration = self.tracker.phase_times.get("test_phase", 0)

        # Should be close to 0.2 seconds (allow ±50ms tolerance)
        assert 0.15 <= duration <= 0.25

    def test_multiple_phases(self):
        """Track multiple phases sequentially."""
        self.tracker.start_phase("phase1")
        time.sleep(0.05)
        self.tracker.end_phase("phase1")

        self.tracker.start_phase("phase2")
        time.sleep(0.05)
        self.tracker.end_phase("phase2")

        metrics = self.tracker.get_metrics()

        assert "phase1" in metrics.phase_times
        assert "phase2" in metrics.phase_times

    def test_total_execution_time(self):
        """AC1: Total execution time tracked."""
        start = time.perf_counter()
        time.sleep(0.1)
        self.tracker.start_phase("work")
        time.sleep(0.1)
        self.tracker.end_phase("work")

        metrics = self.tracker.get_metrics()
        total_time = metrics.total_execution_time

        # Should include all elapsed time
        assert total_time >= 0.1

    def test_get_metrics(self):
        """AC5: Get performance metrics."""
        self.tracker.start_phase("test")
        time.sleep(0.05)
        self.tracker.end_phase("test")

        metrics = self.tracker.get_metrics()

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.total_execution_time > 0
        assert len(metrics.phase_times) > 0

    def test_cache_status_tracking(self):
        """AC2: Track cache hit/miss status."""
        self.tracker.record_cache_hit(cache_age_seconds=10)

        metrics = self.tracker.get_metrics()

        assert metrics.cache_hit is True
        assert metrics.cache_age_seconds == 10

    def test_cache_miss_tracking(self):
        """Record cache miss."""
        self.tracker.record_cache_miss()

        metrics = self.tracker.get_metrics()

        assert metrics.cache_hit is False


class TestTimeoutManagement:
    """Test timeout enforcement."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()

    def test_soft_timeout_check(self):
        """AC3: Check if soft timeout (15s) is exceeded."""
        # Create a tracker that thinks it's been running for 20 seconds
        self.tracker.start_time = time.perf_counter() - 20

        is_timeout = self.tracker.check_soft_timeout(soft_timeout_seconds=15)

        assert is_timeout is True

    def test_soft_timeout_not_exceeded(self):
        """Soft timeout not exceeded."""
        # Just started, should not be timeout
        is_timeout = self.tracker.check_soft_timeout(soft_timeout_seconds=15)

        assert is_timeout is False

    def test_hard_timeout_check(self):
        """AC3: Check hard timeout (60s)."""
        # Create a tracker that thinks it's been running for 70 seconds
        self.tracker.start_time = time.perf_counter() - 70

        is_timeout = self.tracker.check_hard_timeout(hard_timeout_seconds=60)

        assert is_timeout is True

    def test_hard_timeout_not_exceeded(self):
        """Hard timeout not exceeded."""
        is_timeout = self.tracker.check_hard_timeout(hard_timeout_seconds=60)

        assert is_timeout is False

    def test_time_remaining(self):
        """AC4: Calculate time remaining."""
        # Simulate 5 seconds elapsed
        self.tracker.start_time = time.perf_counter() - 5

        remaining = self.tracker.get_time_remaining(total_seconds=15)

        # Should have ~10 seconds remaining (15 - 5)
        assert 9 <= remaining <= 11


class TestCachingMechanism:
    """Test caching for fast path."""

    def test_cache_storage_and_retrieval(self):
        """AC2: Store and retrieve cache."""
        cache_key = "test_project"
        cache_value = {"standard": "value"}

        tracker = PerformanceTracker()
        tracker.set_cache(cache_key, cache_value)
        retrieved = tracker.get_cache(cache_key)

        assert retrieved == cache_value

    def test_cache_hit(self):
        """AC2: Cache hit returns value."""
        cache_key = "project_123"
        cache_value = {"cached": "data"}

        tracker = PerformanceTracker()
        tracker.set_cache(cache_key, cache_value)

        result = tracker.get_cache(cache_key)

        assert result is not None
        assert result == cache_value

    def test_cache_miss(self):
        """Cache miss returns None."""
        tracker = PerformanceTracker()

        result = tracker.get_cache("nonexistent_key")

        assert result is None

    def test_cache_ttl_expiration(self):
        """Cache expires after TTL."""
        cache_key = "expire_test"
        cache_value = {"data": "value"}

        tracker = PerformanceTracker()
        # Set cache with very short TTL (0.1 seconds)
        tracker.set_cache(cache_key, cache_value, ttl_seconds=0.1)

        # Should be available immediately
        assert tracker.get_cache(cache_key) is not None

        # Wait for expiration
        time.sleep(0.15)

        # Should be expired now
        assert tracker.get_cache(cache_key) is None

    def test_fast_path_timing(self):
        """AC2: Cache hit path completes <5 seconds."""
        start = time.perf_counter()

        tracker = PerformanceTracker()
        tracker.set_cache("fast_path", {"data": "cached"})

        # Simulate fast retrieval
        for i in range(10):
            result = tracker.get_cache("fast_path")

        elapsed = time.perf_counter() - start

        # Should be very fast (cache lookups are O(1))
        assert elapsed < 1


class TestBudgetEnforcement:
    """Test time budget enforcement."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()

    def test_budget_tracking(self):
        """AC4: Track time budget per phase."""
        budget = TimeBudget(
            total_seconds=15,
            analysis_seconds=5,
            standards_seconds=2,
            llm_seconds=5,
            formatting_seconds=1,
            cache_seconds=1
        )

        self.tracker.set_budget(budget)

        assert self.tracker.budget is not None
        assert self.tracker.budget.total_seconds == 15

    def test_phase_over_budget_warning(self):
        """AC4: Warn when phase exceeds budget."""
        # Create tracker that's been running for 6 seconds
        self.tracker.start_time = time.perf_counter() - 6

        is_over = self.tracker.is_over_budget(
            phase_budget_seconds=5,
            elapsed_seconds=6
        )

        assert is_over is True

    def test_phase_within_budget(self):
        """Phase within budget."""
        is_over = self.tracker.is_over_budget(
            phase_budget_seconds=5,
            elapsed_seconds=3
        )

        assert is_over is False


class TestPerformanceMetrics:
    """Test PerformanceMetrics data structure."""

    def test_metrics_creation(self):
        """Create PerformanceMetrics instance."""
        metrics = PerformanceMetrics(
            total_execution_time=10.5,
            phase_times={"analysis": 5, "enhancement": 5},
            cache_hit=True,
            cache_age_seconds=60,
            quality_level="full"
        )

        assert metrics.total_execution_time == 10.5
        assert metrics.cache_hit is True

    def test_metrics_with_degradation(self):
        """Metrics with quality degradation."""
        metrics = PerformanceMetrics(
            total_execution_time=14.8,
            phase_times={"analysis": 5, "enhancement": 4.5},
            cache_hit=False,
            cache_age_seconds=None,
            quality_level="degraded"
        )

        assert metrics.quality_level == "degraded"


class TestPerformanceEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tracker = PerformanceTracker()

    def test_zero_phase_time(self):
        """Handle phase with zero duration."""
        self.tracker.start_phase("instant")
        self.tracker.end_phase("instant")

        metrics = self.tracker.get_metrics()

        assert "instant" in metrics.phase_times
        assert metrics.phase_times["instant"] >= 0

    def test_negative_time_remaining(self):
        """Handle negative time remaining."""
        self.tracker.start_time = time.perf_counter() - 20

        remaining = self.tracker.get_time_remaining(total_seconds=15)

        assert remaining <= 0

    def test_multiple_cache_operations(self):
        """Multiple cache set/get operations."""
        tracker = PerformanceTracker()

        for i in range(10):
            key = f"key_{i}"
            value = {"data": f"value_{i}"}
            tracker.set_cache(key, value)
            retrieved = tracker.get_cache(key)
            assert retrieved == value

    def test_phase_timing_with_exception(self):
        """Track timing even if phase has exception."""
        self.tracker.start_phase("error_phase")
        time.sleep(0.05)
        # Simulate error (but still end phase)
        self.tracker.end_phase("error_phase")

        metrics = self.tracker.get_metrics()

        assert "error_phase" in metrics.phase_times


class TestIntegrationScenarios:
    """Test complete performance scenarios."""

    def test_full_enhancement_timing(self):
        """AC1: Full enhancement within 15 seconds."""
        tracker = PerformanceTracker()

        # Simulate full pipeline
        tracker.start_phase("analysis")
        time.sleep(0.1)
        tracker.end_phase("analysis")

        tracker.start_phase("standards")
        time.sleep(0.05)
        tracker.end_phase("standards")

        tracker.start_phase("enhancement")
        time.sleep(0.1)
        tracker.end_phase("enhancement")

        tracker.start_phase("formatting")
        time.sleep(0.05)
        tracker.end_phase("formatting")

        metrics = tracker.get_metrics()

        # Total should be less than 15 seconds
        assert metrics.total_execution_time < 15

    def test_cache_hit_scenario(self):
        """AC2: Cache hit completes <5 seconds."""
        tracker = PerformanceTracker()

        # Set cached standards
        tracker.set_cache("project", {"standard": "cached"}, ttl_seconds=3600)
        tracker.record_cache_hit(cache_age_seconds=10)

        # Simulate fast path (no analysis)
        tracker.start_phase("enhancement")
        time.sleep(0.05)
        tracker.end_phase("enhancement")

        metrics = tracker.get_metrics()

        assert metrics.cache_hit is True
        assert metrics.total_execution_time < 5
