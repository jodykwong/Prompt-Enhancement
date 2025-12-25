"""
AgentsWriter - Writes generated AGENTS.md to project root with backup.

This module handles the final step of the AGENTS.md generation process:
writing the generated content to the project root, backing up existing files,
and validating the output.

Phase 4 Task: AGENTS.md File Writing
"""

import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


class AgentsWriter:
    """
    Writes generated AGENTS.md content to project root.

    This class handles:
    - Backing up existing AGENTS.md files
    - Writing new AGENTS.md content
    - Validating generated content
    - Reporting write results

    Attributes:
        project_root: Root directory of the project
        backup_dir: Directory for storing backups
    """

    def __init__(self, project_root: str, backup_dir: Optional[str] = None):
        """
        Initialize the AGENTS.md writer.

        Args:
            project_root: Path to the project root directory
            backup_dir: Optional directory for backups (default: .agents_backup)
        """
        self.project_root = Path(project_root)
        self.backup_dir = (
            Path(backup_dir) if backup_dir else self.project_root / ".agents_backup"
        )
        self.agents_file = self.project_root / "AGENTS.md"

    def write_agents_md(
        self, content: str, backup_existing: bool = True
    ) -> Tuple[bool, str]:
        """
        Write AGENTS.md to project root.

        Args:
            content: Generated AGENTS.md content
            backup_existing: Whether to backup existing AGENTS.md

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate content
            if not self._validate_content(content):
                return False, "Generated content validation failed"

            # Backup existing file if it exists
            if backup_existing and self.agents_file.exists():
                backup_path = self._create_backup()
                if backup_path:
                    logger.info(f"Backed up existing AGENTS.md to {backup_path}")

            # Write new content
            self._write_file(content)
            logger.info(f"Successfully wrote AGENTS.md to {self.agents_file}")

            return True, f"AGENTS.md successfully written to {self.agents_file}"

        except Exception as e:
            logger.error(f"Failed to write AGENTS.md: {e}")
            return False, f"Error writing AGENTS.md: {str(e)}"

    def restore_from_backup(
        self, backup_timestamp: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Restore AGENTS.md from a backup.

        Args:
            backup_timestamp: Optional specific backup to restore
                             (format: YYYYMMDD_HHMMSS)
                             If None, restores the most recent backup

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            if not self.backup_dir.exists():
                return False, f"No backup directory found at {self.backup_dir}"

            # Find backup files
            backup_files = list(self.backup_dir.glob("AGENTS.md.backup_*"))
            if not backup_files:
                return False, "No AGENTS.md backups found"

            if backup_timestamp:
                # Look for specific backup
                specific_backup = (
                    self.backup_dir / f"AGENTS.md.backup_{backup_timestamp}"
                )
                if not specific_backup.exists():
                    return False, f"Backup {backup_timestamp} not found"
                backup_path = specific_backup
            else:
                # Use most recent backup
                backup_path = max(backup_files, key=lambda p: p.stat().st_mtime)

            # Restore from backup
            with open(backup_path, "r") as f:
                content = f.read()

            self._write_file(content)
            logger.info(f"Restored AGENTS.md from {backup_path}")
            return True, f"Successfully restored AGENTS.md from {backup_path}"

        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False, f"Error restoring backup: {str(e)}"

    def _create_backup(self) -> Optional[Path]:
        """
        Create a backup of the existing AGENTS.md.

        Returns:
            Path to backup file if successful, None otherwise
        """
        try:
            # Create backup directory if it doesn't exist
            self.backup_dir.mkdir(parents=True, exist_ok=True)

            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_dir / f"AGENTS.md.backup_{timestamp}"

            # Copy existing file
            shutil.copy2(self.agents_file, backup_path)
            logger.info(f"Created backup: {backup_path}")

            return backup_path

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None

    def _write_file(self, content: str) -> None:
        """
        Write content to AGENTS.md file.

        Args:
            content: Content to write

        Raises:
            IOError: If writing fails
        """
        self.agents_file.write_text(content, encoding="utf-8")

    def _validate_content(self, content: str) -> bool:
        """
        Validate generated AGENTS.md content.

        Checks:
        - Content is not empty
        - Contains required sections
        - Has valid markdown

        Args:
            content: Content to validate

        Returns:
            True if valid, False otherwise
        """
        if not content or len(content.strip()) == 0:
            logger.error("Generated content is empty")
            return False

        # Check for required sections
        required_sections = ["Setup", "Commands", "Code", "Boundaries"]
        missing_sections = [
            section
            for section in required_sections
            if section.lower() not in content.lower()
        ]

        if missing_sections:
            logger.warning(f"Generated content missing sections: {missing_sections}")
            # Don't fail validation - some templates may not have all sections

        # Check for proper markdown structure
        if not content.startswith("#"):
            logger.warning("Generated content doesn't start with markdown header")

        # Check for unreplaced placeholders (common mistake)
        if "{" in content and "}" in content:
            logger.warning("Generated content may contain unreplaced placeholders")

        return True

    def get_backup_history(self) -> list:
        """
        Get list of available backups.

        Returns:
            List of backup file info (path, timestamp, size)
        """
        backups = []

        if not self.backup_dir.exists():
            return backups

        backup_files = sorted(
            self.backup_dir.glob("AGENTS.md.backup_*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )

        for backup_path in backup_files:
            stat = backup_path.stat()
            timestamp = datetime.fromtimestamp(stat.st_mtime)
            backups.append(
                {
                    "path": str(backup_path),
                    "timestamp": timestamp.isoformat(),
                    "size": stat.st_size,
                }
            )

        return backups

    def cleanup_old_backups(self, keep_count: int = 5) -> Tuple[int, str]:
        """
        Remove old backups keeping only the most recent ones.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            Tuple of (deleted_count: int, message: str)
        """
        try:
            if not self.backup_dir.exists():
                return 0, "No backup directory to clean"

            backup_files = sorted(
                self.backup_dir.glob("AGENTS.md.backup_*"),
                key=lambda p: p.stat().st_mtime,
                reverse=True,
            )

            deleted_count = 0
            for backup_path in backup_files[keep_count:]:
                backup_path.unlink()
                logger.info(f"Deleted old backup: {backup_path}")
                deleted_count += 1

            message = f"Deleted {deleted_count} old backups, kept {min(len(backup_files), keep_count)}"
            logger.info(message)

            return deleted_count, message

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0, f"Error cleaning up backups: {str(e)}"

    def create_summary(self) -> str:
        """
        Create a summary of the write operation.

        Returns:
            Summary string with file info and backup details
        """
        summary_lines = [
            "=" * 60,
            "AGENTS.md Generation Summary",
            "=" * 60,
            f"Project Root: {self.project_root}",
            f"AGENTS.md Path: {self.agents_file}",
            f"File Exists: {self.agents_file.exists()}",
        ]

        if self.agents_file.exists():
            stat = self.agents_file.stat()
            summary_lines.append(f"File Size: {stat.st_size} bytes")
            summary_lines.append(
                f"Last Modified: {datetime.fromtimestamp(stat.st_mtime).isoformat()}"
            )

        backups = self.get_backup_history()
        summary_lines.extend(
            [
                f"",
                f"Backup Directory: {self.backup_dir}",
                f"Total Backups: {len(backups)}",
            ]
        )

        if backups:
            summary_lines.append("Recent Backups:")
            for backup in backups[:3]:
                summary_lines.append(
                    f"  - {backup['timestamp']} ({backup['size']} bytes)"
                )

        summary_lines.append("=" * 60)

        return "\n".join(summary_lines)
