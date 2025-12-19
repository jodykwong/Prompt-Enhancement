"""
Test suite for file access handler with permission error handling.
Tests graceful degradation and access restriction reporting.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from prompt_enhancement.pipeline.file_access import (
    FileAccessHandler,
    FileAccessReport,
)


class TestFileAccessBasics:
    """Test basic file access functionality"""

    def test_successful_file_read(self):
        """Test reading an accessible file"""
        handler = FileAccessHandler()

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            f.write("test content")
            temp_path = f.name

        try:
            content = handler.try_read_file(temp_path)
            assert content == "test content"
            assert handler.files_successfully_accessed == 1
            assert handler.total_files_attempted == 1
            assert handler.files_access_denied == 0
        finally:
            os.unlink(temp_path)

    def test_read_nonexistent_file(self):
        """Test reading a file that doesn't exist"""
        handler = FileAccessHandler()

        content = handler.try_read_file("/nonexistent/path/file.txt")
        assert content is None
        assert handler.files_successfully_accessed == 0
        assert handler.total_files_attempted == 1
        assert handler.files_access_denied == 1
        assert "/nonexistent/path/file.txt" in handler.inaccessible_paths

    def test_read_directory_as_file(self):
        """Test attempting to read directory as file"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            content = handler.try_read_file(temp_dir)
            assert content is None
            assert handler.files_access_denied == 1
            assert temp_dir in handler.inaccessible_paths

    def test_binary_file_handling(self):
        """Test handling of binary files"""
        handler = FileAccessHandler()

        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.bin') as f:
            f.write(b'\x89PNG\r\n\x1a\n')  # PNG header
            temp_path = f.name

        try:
            content = handler.try_read_file(temp_path)
            assert content is None
            assert handler.files_access_denied == 1
        finally:
            os.unlink(temp_path)

    def test_unicode_file_reading(self):
        """Test reading files with various encodings"""
        handler = FileAccessHandler()

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
            f.write("Unicode: ñáéíóú 中文")
            temp_path = f.name

        try:
            content = handler.try_read_file(temp_path)
            assert "Unicode" in content
            assert "中文" in content
            assert handler.files_successfully_accessed == 1
        finally:
            os.unlink(temp_path)


class TestPermissionHandling:
    """Test permission error handling"""

    def test_permission_error_caught(self):
        """Test that PermissionError is caught gracefully"""
        handler = FileAccessHandler()

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = PermissionError("Access denied")
            content = handler.try_read_file("/some/file.txt")

            assert content is None
            assert handler.files_access_denied == 1
            assert handler.total_files_attempted == 1

    def test_os_error_caught(self):
        """Test that OSError is caught gracefully"""
        handler = FileAccessHandler()

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = OSError("I/O error")
            content = handler.try_read_file("/some/file.txt")

            assert content is None
            assert handler.files_access_denied == 1

    def test_unexpected_exception_caught(self):
        """Test that unexpected exceptions don't crash"""
        handler = FileAccessHandler()

        with patch('builtins.open') as mock_open:
            mock_open.side_effect = RuntimeError("Unexpected error")
            content = handler.try_read_file("/some/file.txt")

            assert content is None
            assert handler.files_access_denied == 1
            assert handler.total_files_attempted == 1


class TestDirectoryScanning:
    """Test directory scanning functionality"""

    def test_scan_accessible_directory(self):
        """Test scanning directory with accessible files"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = Path(temp_dir) / "file1.txt"
            file2 = Path(temp_dir) / "file2.py"
            file1.write_text("content1")
            file2.write_text("content2")

            accessible, denied = handler.safe_scan_directory(temp_dir, "*.txt")
            assert len(accessible) >= 1
            assert str(file1) in accessible
            assert len(denied) == 0

    def test_scan_with_glob_pattern(self):
        """Test directory scanning with glob pattern"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            py_file = Path(temp_dir) / "module.py"
            txt_file = Path(temp_dir) / "readme.txt"
            py_file.write_text("code")
            txt_file.write_text("text")

            # Scan for Python files only
            accessible, denied = handler.safe_scan_directory(temp_dir, "*.py")
            assert any("module.py" in f for f in accessible)
            assert not any("readme.txt" in f for f in accessible)

    def test_scan_recursive_directories(self):
        """Test recursive directory scanning"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            (Path(temp_dir) / "root.py").write_text("root")
            (subdir / "nested.py").write_text("nested")

            accessible, denied = handler.safe_scan_directory(temp_dir, "*.py", recursive=True)
            assert len(accessible) >= 2
            assert any("root.py" in f for f in accessible)
            assert any("nested.py" in f for f in accessible)

    def test_scan_nonrecursive(self):
        """Test non-recursive directory scanning"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create nested structure
            subdir = Path(temp_dir) / "subdir"
            subdir.mkdir()
            (Path(temp_dir) / "root.py").write_text("root")
            (subdir / "nested.py").write_text("nested")

            accessible, denied = handler.safe_scan_directory(temp_dir, "*.py", recursive=False)
            # Should only find root.py, not nested.py
            assert any("root.py" in f for f in accessible)
            assert not any("nested.py" in f for f in accessible)

    def test_scan_nonexistent_directory(self):
        """Test scanning nonexistent directory"""
        handler = FileAccessHandler()

        accessible, denied = handler.safe_scan_directory("/nonexistent/dir")
        assert len(accessible) == 0
        assert "/nonexistent/dir" in denied

    def test_scan_with_depth_limit(self):
        """Test directory scanning with depth limit"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create deep nested structure
            deep = Path(temp_dir) / "a" / "b" / "c"
            deep.mkdir(parents=True)
            (Path(temp_dir) / "level0.py").write_text("level0")
            (Path(temp_dir) / "a" / "level1.py").write_text("level1")
            (Path(temp_dir) / "a" / "b" / "level2.py").write_text("level2")
            (deep / "level3.py").write_text("level3")

            # Test with max_depth=1 vs no limit
            accessible_limited, _ = handler.safe_scan_directory(
                temp_dir, "*.py", recursive=True, max_depth=1
            )

            # Reset handler
            handler.reset()

            accessible_unlimited, _ = handler.safe_scan_directory(
                temp_dir, "*.py", recursive=True
            )

            # Limited should find fewer files than unlimited
            assert len(accessible_limited) < len(accessible_unlimited)
            # Should at least find root level file
            assert any("level0.py" in f for f in accessible_limited)


class TestAccessReport:
    """Test file access report generation"""

    def test_report_perfect_access(self):
        """Test report with 100% file access"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file1.txt"
            file1.write_text("content")
            handler.try_read_file(str(file1))

            report = handler.get_access_report()
            assert report.total_files_attempted == 1
            assert report.files_successfully_accessed == 1
            assert report.files_access_denied == 0
            assert report.access_coverage_percentage == 100.0
            assert report.quality_assessment == "complete"
            assert report.confidence_adjustment == 1.0

    def test_report_high_access_coverage(self):
        """Test report with 80%+ access coverage"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 85
        handler.files_access_denied = 15

        report = handler.get_access_report()
        assert report.access_coverage_percentage == 85.0
        assert report.quality_assessment == "complete"
        assert report.confidence_adjustment == 1.0

    def test_report_medium_access_coverage(self):
        """Test report with 60-80% access coverage"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 75
        handler.files_access_denied = 25

        report = handler.get_access_report()
        assert report.access_coverage_percentage == 75.0
        assert report.quality_assessment == "partial"
        assert report.confidence_adjustment == 0.90

    def test_report_low_access_coverage(self):
        """Test report with 40-60% access coverage"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 50
        handler.files_access_denied = 50

        report = handler.get_access_report()
        assert report.access_coverage_percentage == 50.0
        assert report.quality_assessment == "partial"
        assert report.confidence_adjustment == 0.80

    def test_report_very_low_access_coverage(self):
        """Test report with <40% access coverage"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 30
        handler.files_access_denied = 70

        report = handler.get_access_report()
        assert report.access_coverage_percentage == 30.0
        assert report.quality_assessment == "limited"
        assert report.confidence_adjustment == 0.70

    def test_report_with_inaccessible_paths(self):
        """Test report includes inaccessible paths"""
        handler = FileAccessHandler()
        handler.inaccessible_paths = ["/path/denied1", "/path/denied2"]
        handler.files_access_denied = 2
        handler.total_files_attempted = 10
        handler.files_successfully_accessed = 8

        report = handler.get_access_report()
        assert len(report.inaccessible_paths) == 2
        assert "/path/denied1" in report.inaccessible_paths

    def test_report_recommendations(self):
        """Test report includes recommendations for low access"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 50
        handler.files_access_denied = 50
        handler.inaccessible_paths = ["path1", "path2"] * 25

        report = handler.get_access_report()
        assert len(report.recommendations) > 0
        assert any("inaccessible" in rec.lower() for rec in report.recommendations)

    def test_report_small_sample_warning(self):
        """Test report warns about small sample size"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 5
        handler.files_successfully_accessed = 5

        report = handler.get_access_report()
        assert any("small" in rec.lower() for rec in report.recommendations)

    def test_report_format(self):
        """Test report has correct data structure"""
        handler = FileAccessHandler()

        report = handler.get_access_report()
        assert isinstance(report, FileAccessReport)
        assert hasattr(report, 'total_files_attempted')
        assert hasattr(report, 'files_successfully_accessed')
        assert hasattr(report, 'files_access_denied')
        assert hasattr(report, 'access_coverage_percentage')
        assert hasattr(report, 'quality_assessment')
        assert hasattr(report, 'confidence_adjustment')
        assert hasattr(report, 'timestamp')
        assert hasattr(report, 'version')


class TestConfidenceAdjustment:
    """Test confidence score adjustment based on access"""

    def test_no_adjustment_high_access(self):
        """Test no confidence adjustment with high access"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 85
        handler.files_access_denied = 15

        report = handler.get_access_report()
        base_confidence = 0.85
        adjusted = base_confidence * report.confidence_adjustment
        assert abs(adjusted - 0.85) < 0.01

    def test_10_percent_adjustment_medium_access(self):
        """Test 10% confidence reduction with 60-80% access"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 70
        handler.files_access_denied = 30

        report = handler.get_access_report()
        base_confidence = 0.80
        adjusted = base_confidence * report.confidence_adjustment
        assert abs(adjusted - 0.72) < 0.01  # 0.80 * 0.90

    def test_20_percent_adjustment_low_access(self):
        """Test 20% confidence reduction with 40-60% access"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 50
        handler.files_access_denied = 50

        report = handler.get_access_report()
        base_confidence = 0.80
        adjusted = base_confidence * report.confidence_adjustment
        assert abs(adjusted - 0.64) < 0.01  # 0.80 * 0.80

    def test_30_percent_adjustment_very_low_access(self):
        """Test 30% confidence reduction with <40% access"""
        handler = FileAccessHandler()
        handler.total_files_attempted = 100
        handler.files_successfully_accessed = 30
        handler.files_access_denied = 70

        report = handler.get_access_report()
        base_confidence = 0.80
        adjusted = base_confidence * report.confidence_adjustment
        assert abs(adjusted - 0.56) < 0.01  # 0.80 * 0.70


class TestHandlerReset:
    """Test handler reset functionality"""

    def test_reset_clears_statistics(self):
        """Test that reset clears all statistics"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file.txt"
            file1.write_text("content")
            handler.try_read_file(str(file1))

            assert handler.total_files_attempted == 1
            assert handler.files_successfully_accessed == 1

            handler.reset()

            assert handler.total_files_attempted == 0
            assert handler.files_successfully_accessed == 0
            assert handler.files_access_denied == 0
            assert len(handler.inaccessible_paths) == 0


class TestIntegration:
    """Integration tests for file access handler"""

    def test_multiple_read_operations(self):
        """Test multiple read operations accumulate statistics"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            files = []
            for i in range(5):
                file_path = Path(temp_dir) / f"file{i}.txt"
                file_path.write_text(f"content{i}")
                files.append(str(file_path))

            for file_path in files:
                handler.try_read_file(file_path)

            assert handler.total_files_attempted == 5
            assert handler.files_successfully_accessed == 5

    def test_mixed_success_and_failure(self):
        """Test mix of successful and failed file operations"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create accessible file
            file1 = Path(temp_dir) / "file1.txt"
            file1.write_text("content")

            # Try accessible file
            handler.try_read_file(str(file1))

            # Try inaccessible file
            handler.try_read_file("/nonexistent/file.txt")

            assert handler.total_files_attempted == 2
            assert handler.files_successfully_accessed == 1
            assert handler.files_access_denied == 1

            report = handler.get_access_report()
            assert report.access_coverage_percentage == 50.0

    def test_directory_scanning_with_permission_errors(self):
        """Test directory scanning handles permission errors gracefully"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create file
            file1 = Path(temp_dir) / "file.txt"
            file1.write_text("content")

            # Scan directory
            accessible, denied = handler.safe_scan_directory(temp_dir)

            # Should succeed with at least one file
            assert len(accessible) >= 1

    def test_handler_tracks_attempted_paths(self):
        """Test handler tracks all attempted paths"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            file1 = Path(temp_dir) / "file1.txt"
            file1.write_text("content")
            handler.try_read_file(str(file1))
            handler.try_read_file("/nonexistent/file.txt")

            assert len(handler.attempted_paths) == 2
            assert handler.attempted_paths[str(file1)] is True
            assert handler.attempted_paths["/nonexistent/file.txt"] is False


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_directory_scan(self):
        """Test scanning empty directory"""
        handler = FileAccessHandler()

        with tempfile.TemporaryDirectory() as temp_dir:
            accessible, denied = handler.safe_scan_directory(temp_dir)
            assert len(accessible) == 0

    def test_read_empty_file(self):
        """Test reading empty file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            temp_path = Path(temp_dir) / "empty.txt"
            temp_path.write_text("")

            content = handler.try_read_file(str(temp_path))
            assert content == ""
            assert handler.files_successfully_accessed == 1

    def test_read_very_large_file(self):
        """Test reading large file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            temp_path = Path(temp_dir) / "large.txt"
            temp_path.write_text("x" * (1024 * 1024))

            content = handler.try_read_file(str(temp_path))
            assert len(content) == (1024 * 1024)
            assert handler.files_successfully_accessed == 1

    def test_zero_files_attempted(self):
        """Test report with no files attempted"""
        handler = FileAccessHandler()

        report = handler.get_access_report()
        assert report.total_files_attempted == 0
        assert report.access_coverage_percentage == 100.0  # No attempted = no failures


class TestSecurityValidation:
    """Test security features: path traversal protection, file size limits, environment detection"""

    def test_path_traversal_blocked(self):
        """Test that path traversal attacks are blocked"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            # Try to access file outside project root
            content = handler.try_read_file("../../../etc/passwd")
            assert content is None
            assert handler.files_access_denied == 1

    def test_directory_traversal_blocked(self):
        """Test that directory traversal attacks are blocked"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            # Try to scan directory outside project root
            accessible, denied = handler.safe_scan_directory("../../../etc")
            assert len(accessible) == 0
            assert len(denied) == 1

    def test_absolute_path_outside_root_blocked(self):
        """Test that absolute paths outside project root are blocked"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            # Try absolute path outside project
            content = handler.try_read_file("/etc/passwd")
            assert content is None
            assert handler.files_access_denied == 1

    def test_file_size_limit_enforced(self):
        """Test that files exceeding size limit are rejected"""
        handler = FileAccessHandler()

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Write 15MB file (exceeds 10MB limit)
            f.write("x" * (15 * 1024 * 1024))
            temp_path = f.name

        try:
            content = handler.try_read_file(temp_path)
            assert content is None
            assert handler.files_access_denied == 1
            # Check that "too large" is in inaccessible paths tracking
            assert temp_path in handler.inaccessible_paths
        finally:
            os.unlink(temp_path)

    def test_custom_file_size_limit(self):
        """Test custom file size limits"""
        handler = FileAccessHandler()

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("x" * 1000)  # 1KB file
            temp_path = f.name

        try:
            # Try with 500 byte limit
            content = handler.try_read_file(temp_path, max_size=500)
            assert content is None
            assert handler.files_access_denied == 1
        finally:
            os.unlink(temp_path)

    def test_claude_code_environment_detection(self):
        """Test Claude Code environment detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with .claude directory
            claude_dir = Path(temp_dir) / ".claude"
            claude_dir.mkdir()

            handler = FileAccessHandler(project_root=temp_dir)
            assert handler.is_claude_code_env is True

    def test_non_claude_environment(self):
        """Test non-Claude Code environment"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)
            # Without .claude directory and env vars, should be False
            # (unless actually running in Claude Code)
            assert isinstance(handler.is_claude_code_env, bool)

    def test_symlink_loop_protection(self):
        """Test protection against symlink loops"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create symlink loop: a -> b -> a
            dir_a = Path(temp_dir) / "a"
            dir_b = Path(temp_dir) / "b"
            dir_a.mkdir()
            dir_b.mkdir()

            link_in_a = dir_a / "link_to_b"
            link_in_b = dir_b / "link_to_a"

            try:
                link_in_a.symlink_to(dir_b)
                link_in_b.symlink_to(dir_a)

                handler = FileAccessHandler(project_root=temp_dir)

                # Should not hang or crash
                accessible, denied = handler.safe_scan_directory(temp_dir, recursive=True)
                # Should complete without infinite loop
                assert isinstance(accessible, list)
            except OSError:
                # Symlink creation might fail on some systems, skip test
                pass

    def test_malicious_glob_pattern_handled(self):
        """Test that malicious glob patterns don't cause issues"""
        with tempfile.TemporaryDirectory() as temp_dir:
            handler = FileAccessHandler(project_root=temp_dir)

            # Create a test file
            test_file = Path(temp_dir) / "test.txt"
            test_file.write_text("content")

            # Try various patterns (should handle gracefully)
            patterns = ["**/*", "**/.*", "**/..*", "*.txt"]
            for pattern in patterns:
                accessible, denied = handler.safe_scan_directory(temp_dir, pattern=pattern)
                assert isinstance(accessible, list)
                assert isinstance(denied, list)
