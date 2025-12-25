"""Error logging and recovery system."""

import logging
import logging.handlers
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ErrorLog:
    """Error log entry with complete metadata."""

    timestamp: str
    level: str
    category: str
    message: str
    context: str
    project_fingerprint: str
    stack_trace: Optional[str] = None
    thread_id: str = "main"

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "timestamp": self.timestamp,
            "level": self.level,
            "category": self.category,
            "message": self.message,
            "context": self.context,
            "project_fingerprint": self.project_fingerprint,
            "stack_trace": self.stack_trace,
            "thread_id": self.thread_id,
        }


class ErrorLogger:
    """Manages error logging with rotation and protection."""

    # Log level mapping
    LOG_LEVELS = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
    }

    # Sensitive patterns to redact
    SENSITIVE_PATTERNS = [
        (r"OPENAI_API_KEY=[^\s]+", "OPENAI_API_KEY=[REDACTED]"),
        (r"DEEPSEEK_API_KEY=[^\s]+", "DEEPSEEK_API_KEY=[REDACTED]"),
        (r"sk-[a-zA-Z0-9]+", "[REDACTED]"),
        (r"bearer\s+[a-zA-Z0-9]+", "bearer [REDACTED]"),
        (r"authorization=[^\s]+", "authorization=[REDACTED]"),
    ]

    def __init__(self, log_dir: Optional[str] = None, log_level: str = "INFO"):
        """
        Initialize error logger.

        Args:
            log_dir: Directory for logs (default: ~/.prompt-enhancement/logs/)
            log_level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        if log_dir is None:
            log_dir = str(Path.home() / ".prompt-enhancement" / "logs")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "pe.log"

        # Set up rotating file handler (10MB or daily)
        self.handler = logging.handlers.RotatingFileHandler(
            self.log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=7,  # Keep 7 days
        )

        # Set log level
        log_level_int = self.LOG_LEVELS.get(log_level.upper(), logging.INFO)
        self.handler.setLevel(log_level_int)

        # Set format
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.handler.setFormatter(formatter)

        # Get logger and add handler
        self.logger = logging.getLogger("prompt_enhancement.errors")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(log_level_int)

    def log_error(
        self,
        level: str,
        category: str,
        message: str,
        context: str = "",
        project_fingerprint: str = "unknown",
        stack_trace: Optional[str] = None,
    ) -> None:
        """
        Log an error with metadata.

        Args:
            level: Log level (DEBUG, INFO, WARNING, ERROR)
            category: Error category
            message: Error message
            context: Context (what was being attempted)
            project_fingerprint: Project identifier
            stack_trace: Stack trace (if DEBUG level)
        """
        # Redact sensitive information
        message = self._redact_sensitive_data(message)
        context = self._redact_sensitive_data(context)
        if stack_trace:
            stack_trace = self._redact_sensitive_data(stack_trace)

        # Create error log entry
        error_log = ErrorLog(
            timestamp=datetime.utcnow().isoformat() + "Z",
            level=level,
            category=category,
            message=message,
            context=context,
            project_fingerprint=project_fingerprint,
            stack_trace=stack_trace if level == "DEBUG" else None,
        )

        # Log it
        log_level_int = self.LOG_LEVELS.get(level.upper(), logging.INFO)
        log_message = (
            f"[{category}] {message} | "
            f"context: {context} | "
            f"project: {project_fingerprint}"
        )

        self.logger.log(log_level_int, log_message)

    @staticmethod
    def _redact_sensitive_data(text: str) -> str:
        """
        Redact sensitive information from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        if not text:
            return text

        for pattern, replacement in ErrorLogger.SENSITIVE_PATTERNS:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        return text

    def get_recent_logs(
        self,
        limit: int = 50,
        level_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
        keyword_filter: Optional[str] = None,
    ) -> List[str]:
        """
        Get recent log entries.

        Args:
            limit: Maximum number of entries to return
            level_filter: Filter by level (DEBUG, INFO, WARNING, ERROR)
            date_filter: Filter by date (YYYY-MM-DD)
            keyword_filter: Filter by keyword

        Returns:
            List of log lines
        """
        if not self.log_file.exists():
            return []

        with open(self.log_file, "r") as f:
            lines = f.readlines()

        # Filter if specified
        if level_filter:
            lines = [l for l in lines if level_filter.upper() in l]

        if date_filter:
            lines = [l for l in lines if date_filter in l]

        if keyword_filter:
            lines = [l for l in lines if keyword_filter.lower() in l.lower()]

        # Return most recent entries (last N lines)
        return lines[-limit:] if len(lines) > limit else lines

    def get_log_status(self) -> dict:
        """
        Get log file status.

        Returns:
            Dictionary with log status information
        """
        if not self.log_file.exists():
            return {
                "exists": False,
                "path": str(self.log_file),
                "size_mb": 0,
                "retention_days": 7,
            }

        size_mb = self.log_file.stat().st_size / (1024 * 1024)

        # Count backup files
        backup_files = list(self.log_dir.glob("pe.log.*"))
        retention_days = min(len(backup_files), 7)

        return {
            "exists": True,
            "path": str(self.log_file),
            "size_mb": round(size_mb, 2),
            "retention_days": retention_days,
            "backup_count": len(backup_files),
        }


class ProjectFingerprint:
    """Generate stable, anonymized project fingerprints."""

    @staticmethod
    def generate(project_path: Path) -> str:
        """
        Generate stable fingerprint from project characteristics.

        Args:
            project_path: Path to project

        Returns:
            Fingerprint string (e.g., prj_abc123)
        """
        if not project_path.exists():
            return "prj_unknown"

        # Use directory name hash
        import hashlib

        dir_name = project_path.name
        hash_obj = hashlib.md5(dir_name.encode())
        hash_hex = hash_obj.hexdigest()[:6]

        return f"prj_{hash_hex}"


class RecoveryHelper:
    """Provides recovery suggestions for errors."""

    RECOVERY_MAP = {
        "api_key_missing": [
            "Run /pe-setup to configure API key",
            "Or export OPENAI_API_KEY=sk-...",
            "Or add to ~/.prompt-enhancement/config.yaml",
        ],
        "project_not_detected": [
            "Ensure you're in project root directory",
            "Project should contain package.json, requirements.txt, etc.",
            "System will use generic enhancement as fallback",
        ],
        "detection_failed": [
            "Use --override to manually set standards",
            "Create .pe.yaml configuration in project",
            "Run /pe-setup to configure preferences",
        ],
        "api_timeout": [
            "Check your internet connection",
            "Retry the operation",
            "Check API service status if issue persists",
        ],
        "permission_denied": [
            "Check file permissions in your project",
            "Ensure you have read access to project files",
            "Run from a directory with accessible files",
        ],
    }

    @staticmethod
    def get_recovery_steps(category: str) -> List[str]:
        """
        Get recovery steps for an error category.

        Args:
            category: Error category

        Returns:
            List of recovery steps
        """
        return RecoveryHelper.RECOVERY_MAP.get(
            category.lower(),
            [
                "Check logs for detailed information",
                "Retry the operation",
                "Run /pe-help for documentation",
            ],
        )

    @staticmethod
    def format_recovery_message(
        category: str,
        error_message: str = "",
    ) -> str:
        """
        Format complete recovery message.

        Args:
            category: Error category
            error_message: Optional error message

        Returns:
            Formatted recovery message
        """
        steps = RecoveryHelper.get_recovery_steps(category)

        lines = [
            "❌ An Error Occurred",
            "",
            "Diagnostic information saved to:",
            "~/.prompt-enhancement/logs/pe.log",
            "",
            "Suggested steps:",
        ]

        for i, step in enumerate(steps, 1):
            lines.append(f"{i}. {step}")

        lines.extend(
            [
                "",
                "For more help: /pe-help",
            ]
        )

        return "\n".join(lines)
