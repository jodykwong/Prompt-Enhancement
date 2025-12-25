"""
AgentsGenerator - Main entry point for AGENTS.md generation workflow.

This module provides the high-level API for the complete AGENTS.md generation
process, orchestrating all Phase 4 components.

Usage:
    from prompt_enhancement.phase4 import AgentsGenerator

    generator = AgentsGenerator("/path/to/project")
    success, message = generator.generate()
    if success:
        print(f"Success: {message}")
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from .template_generator import AgentsTemplateGenerator
from .agents_writer import AgentsWriter

logger = logging.getLogger(__name__)


class AgentsGenerator:
    """
    Main interface for AGENTS.md generation.

    Orchestrates the complete workflow:
    1. Project analysis and type detection
    2. Template selection
    3. Content extraction
    4. Template filling
    5. File writing with backup

    Attributes:
        project_root: Path to the project root
        generator: Template generator instance
        writer: AGENTS.md writer instance
    """

    def __init__(self, project_root: str, backup_dir: Optional[str] = None):
        """
        Initialize the AGENTS.md generator.

        Args:
            project_root: Path to project root directory
            backup_dir: Optional directory for backups
        """
        self.project_root = Path(project_root)
        if not self.project_root.exists():
            raise ValueError(f"Project root does not exist: {project_root}")

        self.generator = AgentsTemplateGenerator(str(self.project_root))
        self.writer = AgentsWriter(str(self.project_root), backup_dir)

        logger.info(f"Initialized AgentsGenerator for {self.project_root}")

    def generate(self, backup_existing: bool = True) -> Tuple[bool, str]:
        """
        Generate and write AGENTS.md file.

        Complete workflow:
        1. Generate AGENTS.md content
        2. Validate content
        3. Backup existing file (if specified)
        4. Write new file

        Args:
            backup_existing: Whether to backup existing AGENTS.md

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            logger.info("Starting AGENTS.md generation...")

            # Generate content
            logger.debug("Generating AGENTS.md content...")
            content = self.generator.generate_agents_md()

            if not content:
                return False, "Failed to generate AGENTS.md content"

            # Write to file
            logger.debug("Writing AGENTS.md to file...")
            success, message = self.writer.write_agents_md(content, backup_existing)

            if success:
                logger.info(f"Successfully generated AGENTS.md: {message}")
            else:
                logger.error(f"Failed to write AGENTS.md: {message}")

            return success, message

        except Exception as e:
            error_msg = f"Error generating AGENTS.md: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def generate_preview(self) -> Tuple[bool, str]:
        """
        Generate and return AGENTS.md content without writing to file.

        Useful for reviewing generated content before committing.

        Returns:
            Tuple of (success: bool, content: str)
        """
        try:
            logger.info("Generating AGENTS.md preview...")
            content = self.generator.generate_agents_md()

            if not content:
                return False, "Failed to generate content"

            return True, content

        except Exception as e:
            error_msg = f"Error generating preview: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def restore_from_backup(
        self, backup_timestamp: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Restore AGENTS.md from a backup.

        Args:
            backup_timestamp: Optional specific backup timestamp to restore

        Returns:
            Tuple of (success: bool, message: str)
        """
        logger.info("Restoring AGENTS.md from backup...")
        return self.writer.restore_from_backup(backup_timestamp)

    def get_backup_history(self) -> list:
        """
        Get list of available backups.

        Returns:
            List of backup information dictionaries
        """
        return self.writer.get_backup_history()

    def cleanup_old_backups(self, keep_count: int = 5) -> Tuple[int, str]:
        """
        Remove old backups keeping only recent ones.

        Args:
            keep_count: Number of recent backups to keep

        Returns:
            Tuple of (deleted_count: int, message: str)
        """
        logger.info(f"Cleaning up old backups (keeping {keep_count})...")
        return self.writer.cleanup_old_backups(keep_count)

    def get_summary(self) -> str:
        """
        Get a detailed summary of the generation state.

        Returns:
            Summary string with file information and backup details
        """
        return self.writer.create_summary()

    def verify_agents_md(self) -> Tuple[bool, str]:
        """
        Verify that AGENTS.md exists and is valid.

        Returns:
            Tuple of (valid: bool, message: str)
        """
        agents_file = self.project_root / "AGENTS.md"

        if not agents_file.exists():
            return False, "AGENTS.md does not exist"

        try:
            with open(agents_file, "r") as f:
                content = f.read()

            if not content or len(content.strip()) == 0:
                return False, "AGENTS.md is empty"

            # Check for basic markdown structure
            if not content.startswith("#"):
                return False, "AGENTS.md does not start with markdown header"

            # Check for common sections
            sections_count = len(
                [line for line in content.split("\n") if line.startswith("##")]
            )

            return True, f"AGENTS.md is valid ({sections_count} sections found)"

        except Exception as e:
            return False, f"Error verifying AGENTS.md: {str(e)}"


def generate_agents_md(project_root: str, backup: bool = True) -> Tuple[bool, str]:
    """
    Convenience function to generate AGENTS.md in one call.

    Args:
        project_root: Path to project root
        backup: Whether to backup existing AGENTS.md

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        generator = AgentsGenerator(project_root)
        return generator.generate(backup_existing=backup)
    except Exception as e:
        return False, f"Error: {str(e)}"
