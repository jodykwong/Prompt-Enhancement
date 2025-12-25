"""Error handling and recovery system for prompt enhancement."""

from .classification import ErrorCategory, ErrorClassifier
from .messages import UserErrorMessage, ErrorMessageFormatter
from .degradation import DegradationLevel, DegradationInfo, DegradationStrategy
from .confirmation import (
    UserDecision,
    DiagnosticInfo,
    DegradationConfirmation,
    DiagnosticBuilder,
)
from .logging_system import (
    ErrorLog,
    ErrorLogger,
    ProjectFingerprint,
    RecoveryHelper,
)

__all__ = [
    "ErrorCategory",
    "ErrorClassifier",
    "UserErrorMessage",
    "ErrorMessageFormatter",
    "DegradationLevel",
    "DegradationInfo",
    "DegradationStrategy",
    "UserDecision",
    "DiagnosticInfo",
    "DegradationConfirmation",
    "DiagnosticBuilder",
    "ErrorLog",
    "ErrorLogger",
    "ProjectFingerprint",
    "RecoveryHelper",
]
