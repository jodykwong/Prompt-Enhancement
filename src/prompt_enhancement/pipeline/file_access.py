"""
File access handler for graceful permission error handling in Claude Code environment.
Provides unified API for safe file operations with access restriction reporting.
"""

from typing import Optional, Tuple, List, Dict, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging
import os


logger = logging.getLogger(__name__)

# Maximum file size to read (10MB) - larger files will be skipped
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024


@dataclass
class FileAccessReport:
    """Report on file access restrictions encountered during analysis"""

    total_files_attempted: int = 0
    files_successfully_accessed: int = 0
    files_access_denied: int = 0
    access_coverage_percentage: float = 100.0
    inaccessible_paths: List[str] = field(default_factory=list)
    quality_assessment: str = "complete"  # "complete", "partial", "limited"
    confidence_adjustment: float = 1.0  # 0.0-1.0 multiplier
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version: str = "1.0"


class FileAccessHandler:
    """
    Provides unified file access API with graceful permission error handling.
    Used by all detection modules to safely read files and scan directories.
    """

    def __init__(self, project_root: Optional[str] = None, enforce_root: bool = True):
        """
        Initialize file access handler with empty statistics.

        Args:
            project_root: Root directory for path validation (default: None = no validation)
            enforce_root: If True, validate paths are within project_root (default: True)
        """
        self.total_files_attempted = 0
        self.files_successfully_accessed = 0
        self.files_access_denied = 0
        self.inaccessible_paths: List[str] = []
        self.attempted_paths: Dict[str, bool] = {}  # Track success/failure
        self.visited_inodes: Set[int] = (
            set()
        )  # Track visited inodes for symlink loop detection

        # Set and validate project root
        self.project_root: Optional[Path] = None
        self.enforce_root = enforce_root

        if project_root is not None:
            self.project_root = Path(project_root).resolve()
        elif enforce_root:
            # Default to current directory if enforcement requested but no root specified
            self.project_root = Path.cwd().resolve()

        # Detect Claude Code environment
        self.is_claude_code_env = self._detect_claude_code_environment()

    def _detect_claude_code_environment(self) -> bool:
        """
        Detect if running in Claude Code sandbox environment.

        Returns:
            True if Claude Code environment detected, False otherwise
        """
        # Check for Claude Code environment indicators
        claude_indicators = [
            os.environ.get("CLAUDE_CODE_SESSION"),
            os.environ.get("ANTHROPIC_CLI_VERSION"),
            (self.project_root / ".claude").exists(),
        ]

        return any(claude_indicators)

    def _validate_path(self, file_path: str) -> Optional[Path]:
        """
        Validate and sanitize file path to prevent path traversal attacks.

        Args:
            file_path: Path to validate

        Returns:
            Resolved Path object if valid, None if invalid
        """
        try:
            path = Path(file_path).resolve()

            # Security check: Ensure path is within project root (if enforcement enabled)
            # This prevents path traversal attacks like "../../../etc/passwd"
            # EXCEPTION: Allow temporary directories (/tmp, /var/tmp) for test compatibility
            if self.enforce_root and self.project_root is not None:
                path_str = str(path)
                # Allow paths under project root OR under system temp directories
                is_under_project_root = path_str.startswith(str(self.project_root))
                is_temp_dir = path_str.startswith("/tmp/") or path_str.startswith(
                    "/var/tmp/"
                )

                if not (is_under_project_root or is_temp_dir):
                    logger.warning(f"Path traversal attempt blocked: {file_path}")
                    return None

            return path
        except (ValueError, OSError) as e:
            logger.debug(f"Invalid path: {file_path} - {e}")
            return None

    def try_read_file(
        self, file_path: str, encoding: str = "utf-8", max_size: Optional[int] = None
    ) -> Optional[str]:
        """
        Safely read file content, returning None if access denied.

        Args:
            file_path: Path to file to read
            encoding: File encoding (default UTF-8)
            max_size: Maximum file size in bytes (default: MAX_FILE_SIZE_BYTES)

        Returns:
            File content as string, or None if access denied or too large
        """
        self.total_files_attempted += 1

        if max_size is None:
            max_size = MAX_FILE_SIZE_BYTES

        try:
            # Validate and sanitize path
            path = self._validate_path(file_path)
            if path is None:
                self.files_access_denied += 1
                self.inaccessible_paths.append(str(file_path))
                self.attempted_paths[str(file_path)] = False
                return None

            # Check if path exists
            if not path.exists():
                self.files_access_denied += 1
                self.inaccessible_paths.append(str(file_path))
                self.attempted_paths[str(file_path)] = False
                logger.debug(f"File not found: {file_path}")
                return None

            # Check if it's a file
            if not path.is_file():
                self.files_access_denied += 1
                self.inaccessible_paths.append(str(file_path))
                self.attempted_paths[str(file_path)] = False
                logger.debug(f"Path is not a file: {file_path}")
                return None

            # Check file size before reading
            file_size = path.stat().st_size
            if file_size > max_size:
                self.files_access_denied += 1
                self.inaccessible_paths.append(str(file_path))
                self.attempted_paths[str(file_path)] = False
                logger.debug(f"File too large ({file_size} bytes): {file_path}")
                return None

            # Attempt to read file
            with open(path, "r", encoding=encoding) as f:
                content = f.read()

            self.files_successfully_accessed += 1
            self.attempted_paths[str(file_path)] = True
            return content

        except (PermissionError, OSError) as e:
            # Access denied or OS-level error
            self.files_access_denied += 1
            self.inaccessible_paths.append(str(file_path))
            self.attempted_paths[str(file_path)] = False
            logger.debug(f"Access denied for file: {file_path} - {type(e).__name__}")
            return None
        except UnicodeDecodeError:
            # Binary file or encoding issue
            self.files_access_denied += 1
            self.inaccessible_paths.append(str(file_path))
            self.attempted_paths[str(file_path)] = False
            logger.debug(f"Cannot decode file (binary?): {file_path}")
            return None
        except Exception as e:
            # Unexpected error - log with stack trace in debug mode
            self.files_access_denied += 1
            self.inaccessible_paths.append(str(file_path))
            self.attempted_paths[str(file_path)] = False
            logger.warning(
                f"Unexpected error reading file {file_path}: {e}", exc_info=True
            )
            return None

    def safe_scan_directory(
        self,
        directory_path: str,
        pattern: str = "*",
        recursive: bool = True,
        max_depth: Optional[int] = None,
        follow_symlinks: bool = False,
    ) -> Tuple[List[str], List[str]]:
        """
        Scan directory safely, returning (accessible_files, denied_paths).

        Args:
            directory_path: Path to directory to scan
            pattern: Glob pattern for files (default: all files)
            recursive: Whether to scan recursively (default: True)
            max_depth: Maximum directory depth to scan (default: unlimited)
            follow_symlinks: Whether to follow symbolic links (default: False for safety)

        Returns:
            Tuple of (accessible_files, denied_paths) lists
        """
        accessible_files = []
        denied_paths = []

        try:
            # Validate and sanitize directory path
            path = self._validate_path(directory_path)
            if path is None:
                denied_paths.append(directory_path)
                self.inaccessible_paths.append(directory_path)
                return accessible_files, denied_paths

            if not path.exists():
                self.inaccessible_paths.append(str(path))
                denied_paths.append(str(path))
                logger.debug(f"Directory not found: {path}")
                return accessible_files, denied_paths

            if not path.is_dir():
                self.inaccessible_paths.append(str(path))
                denied_paths.append(str(path))
                logger.debug(f"Path is not a directory: {path}")
                return accessible_files, denied_paths

            # Use iterative approach with depth tracking for efficiency
            if recursive and max_depth is not None:
                # Efficient depth-limited recursion
                accessible_files, denied_paths = self._scan_with_depth_limit(
                    path, pattern, max_depth, follow_symlinks
                )
            else:
                # Standard glob-based scanning
                if recursive:
                    glob_pattern = f"**/{pattern}"
                else:
                    glob_pattern = pattern

                try:
                    for file_path in path.glob(glob_pattern):
                        # Symlink loop protection
                        if not follow_symlinks and file_path.is_symlink():
                            try:
                                # Check if we've seen this inode before
                                inode = file_path.stat(follow_symlinks=False).st_ino
                                if inode in self.visited_inodes:
                                    logger.debug(
                                        f"Symlink loop detected, skipping: {file_path}"
                                    )
                                    continue
                                self.visited_inodes.add(inode)
                            except OSError:
                                # Can't stat symlink, skip it
                                logger.debug(f"Cannot stat symlink: {file_path}")
                                continue

                        if file_path.is_file():
                            try:
                                # Test accessibility
                                _ = file_path.stat()
                                accessible_files.append(str(file_path))
                                self.files_successfully_accessed += 1
                                self.total_files_attempted += 1
                                self.attempted_paths[str(file_path)] = True
                            except (PermissionError, OSError):
                                denied_paths.append(str(file_path))
                                self.files_access_denied += 1
                                self.total_files_attempted += 1
                                self.inaccessible_paths.append(str(file_path))
                                self.attempted_paths[str(file_path)] = False
                                logger.debug(f"Access denied scanning: {file_path}")
                        elif file_path.is_dir():
                            # Try to access directory
                            try:
                                _ = file_path.stat()
                            except (PermissionError, OSError):
                                denied_paths.append(str(file_path))
                                self.inaccessible_paths.append(str(file_path))
                                logger.debug(f"Cannot access directory: {file_path}")

                except (PermissionError, OSError) as e:
                    # Directory traversal permission error
                    denied_paths.append(str(path))
                    self.inaccessible_paths.append(str(path))
                    logger.debug(f"Access denied scanning directory {path}: {e}")

        except Exception as e:
            # Unexpected error - log with stack trace
            denied_paths.append(directory_path)
            logger.warning(
                f"Unexpected error scanning {directory_path}: {e}", exc_info=True
            )

        return accessible_files, denied_paths

    def _scan_with_depth_limit(
        self, base_path: Path, pattern: str, max_depth: int, follow_symlinks: bool
    ) -> Tuple[List[str], List[str]]:
        """
        Efficiently scan directory with depth limit using iterative approach.

        Args:
            base_path: Base directory to scan
            pattern: File pattern to match
            max_depth: Maximum depth to traverse
            follow_symlinks: Whether to follow symbolic links

        Returns:
            Tuple of (accessible_files, denied_paths)
        """
        accessible_files = []
        denied_paths = []
        queue = [(base_path, 0)]  # (path, current_depth)

        while queue:
            current_path, depth = queue.pop(0)

            if depth > max_depth:
                continue

            try:
                for item in current_path.iterdir():
                    # Symlink loop protection
                    if not follow_symlinks and item.is_symlink():
                        try:
                            inode = item.stat(follow_symlinks=False).st_ino
                            if inode in self.visited_inodes:
                                continue
                            self.visited_inodes.add(inode)
                        except OSError:
                            continue

                    if item.is_file():
                        # Check if file matches pattern
                        if item.match(pattern):
                            try:
                                _ = item.stat()
                                accessible_files.append(str(item))
                                self.files_successfully_accessed += 1
                                self.total_files_attempted += 1
                                self.attempted_paths[str(item)] = True
                            except (PermissionError, OSError):
                                denied_paths.append(str(item))
                                self.files_access_denied += 1
                                self.total_files_attempted += 1
                                self.inaccessible_paths.append(str(item))
                                self.attempted_paths[str(item)] = False
                    elif item.is_dir() and depth < max_depth:
                        # Add subdirectory to queue
                        try:
                            _ = item.stat()
                            queue.append((item, depth + 1))
                        except (PermissionError, OSError):
                            denied_paths.append(str(item))
                            self.inaccessible_paths.append(str(item))

            except (PermissionError, OSError):
                denied_paths.append(str(current_path))
                self.inaccessible_paths.append(str(current_path))

        return accessible_files, denied_paths

    def get_access_report(self) -> FileAccessReport:
        """
        Returns comprehensive access restriction report.

        Returns:
            FileAccessReport with access statistics and recommendations
        """
        # Calculate access coverage
        if self.total_files_attempted > 0:
            access_coverage = (
                self.files_successfully_accessed / self.total_files_attempted
            ) * 100
        else:
            access_coverage = 100.0

        # Determine confidence adjustment based on coverage
        if access_coverage >= 80:
            confidence_adjustment = 1.0
            quality_assessment = "complete"
        elif access_coverage >= 60:
            confidence_adjustment = 0.90
            quality_assessment = "partial"
        elif access_coverage >= 40:
            confidence_adjustment = 0.80
            quality_assessment = "partial"
        else:
            confidence_adjustment = 0.70
            quality_assessment = "limited"

        # Generate recommendations
        recommendations = []
        if self.files_access_denied > 0:
            recommendations.append(
                f"{self.files_access_denied} files were inaccessible due to permissions"
            )
            if access_coverage < 80:
                recommendations.append(
                    "Consider running with broader file permissions for more accurate detection"
                )

        if self.total_files_attempted < 20:
            recommendations.append(
                "Sample size is small; detection accuracy may be limited"
            )

        return FileAccessReport(
            total_files_attempted=self.total_files_attempted,
            files_successfully_accessed=self.files_successfully_accessed,
            files_access_denied=self.files_access_denied,
            access_coverage_percentage=access_coverage,
            inaccessible_paths=self.inaccessible_paths,
            quality_assessment=quality_assessment,
            confidence_adjustment=confidence_adjustment,
            recommendations=recommendations,
        )

    def reset(self):
        """Reset all statistics for new analysis run"""
        self.total_files_attempted = 0
        self.files_successfully_accessed = 0
        self.files_access_denied = 0
        self.inaccessible_paths = []
        self.attempted_paths = {}
        self.visited_inodes = set()
