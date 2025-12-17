"""
File access handler for graceful permission error handling in Claude Code environment.
Provides unified API for safe file operations with access restriction reporting.
"""

from typing import Optional, Tuple, List, Dict
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import logging
import os


logger = logging.getLogger(__name__)


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

    def __init__(self):
        """Initialize file access handler with empty statistics"""
        self.total_files_attempted = 0
        self.files_successfully_accessed = 0
        self.files_access_denied = 0
        self.inaccessible_paths: List[str] = []
        self.attempted_paths: Dict[str, bool] = {}  # Track success/failure

    def try_read_file(
        self,
        file_path: str,
        encoding: str = "utf-8"
    ) -> Optional[str]:
        """
        Safely read file content, returning None if access denied.

        Args:
            file_path: Path to file to read
            encoding: File encoding (default UTF-8)

        Returns:
            File content as string, or None if access denied
        """
        self.total_files_attempted += 1

        try:
            path = Path(file_path)

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

            # Attempt to read file
            with open(file_path, "r", encoding=encoding) as f:
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
            # Unexpected error - log but don't crash
            self.files_access_denied += 1
            self.inaccessible_paths.append(str(file_path))
            self.attempted_paths[str(file_path)] = False
            logger.warning(f"Unexpected error reading file {file_path}: {e}")
            return None

    def safe_scan_directory(
        self,
        directory_path: str,
        pattern: str = "*",
        recursive: bool = True,
        max_depth: int = None
    ) -> Tuple[List[str], List[str]]:
        """
        Scan directory safely, returning (accessible_files, denied_paths).

        Args:
            directory_path: Path to directory to scan
            pattern: Glob pattern for files (default: all files)
            recursive: Whether to scan recursively (default: True)
            max_depth: Maximum directory depth to scan (default: unlimited)

        Returns:
            Tuple of (accessible_files, denied_paths) lists
        """
        accessible_files = []
        denied_paths = []

        try:
            path = Path(directory_path)

            if not path.exists():
                self.inaccessible_paths.append(directory_path)
                denied_paths.append(directory_path)
                logger.debug(f"Directory not found: {directory_path}")
                return accessible_files, denied_paths

            if not path.is_dir():
                self.inaccessible_paths.append(directory_path)
                denied_paths.append(directory_path)
                logger.debug(f"Path is not a directory: {directory_path}")
                return accessible_files, denied_paths

            # Scan directory
            if recursive:
                glob_pattern = f"**/{pattern}"
            else:
                glob_pattern = pattern

            try:
                for file_path in path.glob(glob_pattern):
                    # Check depth if max_depth specified
                    if max_depth is not None:
                        depth = len(file_path.relative_to(path).parts)
                        if depth > max_depth:
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
                denied_paths.append(directory_path)
                self.inaccessible_paths.append(directory_path)
                logger.debug(f"Access denied scanning directory {directory_path}: {e}")

        except Exception as e:
            # Unexpected error - log but don't crash
            denied_paths.append(directory_path)
            logger.warning(f"Unexpected error scanning {directory_path}: {e}")

        return accessible_files, denied_paths

    def get_access_report(self) -> FileAccessReport:
        """
        Returns comprehensive access restriction report.

        Returns:
            FileAccessReport with access statistics and recommendations
        """
        # Calculate access coverage
        if self.total_files_attempted > 0:
            access_coverage = (self.files_successfully_accessed / self.total_files_attempted) * 100
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
