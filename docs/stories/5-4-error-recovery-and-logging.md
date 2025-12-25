# Story 5.4: Error Recovery and Logging

**Epic**: Epic 5: Robust Error Handling & Graceful Degradation
**Priority**: High
**Acceptance Criteria**: 6
**Status**: Ready for Development

## Overview

Every error must be logged with complete information for debugging, while sensitive data is always protected. Users receive recovery suggestions based on the error type. Logs rotate automatically and are retained for 7 days.

## Acceptance Criteria

### AC1: Error Logging with Complete Metadata

**Given** any error occurs
**When** handling error
**Then** system logs:
- Timestamp in ISO 8601 format (e.g., 2024-01-15T14:30:45.123Z)
- Error category (API_KEY_MISSING, PROJECT_NOT_DETECTED, etc.)
- Error message (user-friendly version)
- Stack trace (DEBUG mode only, never in production)
- Project fingerprint (for project identification without exposing paths)
- Error context (what was being attempted)

**Example Log Entry:**
```json
{
  "timestamp": "2024-01-15T14:30:45.123Z",
  "level": "ERROR",
  "category": "PROJECT_NOT_DETECTED",
  "message": "Unable to identify project type",
  "context": "Detection attempted for /home/user/myproject",
  "project_fingerprint": "prj_abc123",
  "stack_trace": null,
  "thread_id": "main"
}
```

---

### AC2: Log Level Configuration

**Given** log level configuration
**When** logging errors
**Then** system supports 4 levels:

1. **DEBUG**: All detailed information (development use)
   - Stack traces included
   - All debug messages logged
   - Verbose output

2. **INFO**: Key events (standard/default)
   - Errors and warnings logged
   - Debug messages excluded
   - Normal operation tracking

3. **WARNING**: Warnings and errors only
   - Only warnings and errors
   - Info messages excluded
   - Minimal logging

4. **ERROR**: Errors only
   - Only critical errors
   - No warnings or info
   - Silent operation

**Configuration Methods:**
- Environment variable: `PE_LOG_LEVEL=DEBUG`
- Config file: `~/.prompt-enhancement/config.yaml` with `log_level: debug`
- Command-line flag: `--log-level debug`

---

### AC3: Log Storage and Rotation

**Given** log storage location
**When** writing logs
**Then** system:
- Writes to `~/.prompt-enhancement/logs/pe.log`
- Rotates logs when:
  - Daily at midnight UTC, OR
  - File reaches 10MB (whichever comes first)
- Retains last 7 days of logs (deletes older files)
- Creates directory if not exists
- Creates new log file if rotation happens mid-session

**Log File Naming Convention:**
```
pe.log                     (current log)
pe.log.2024-01-15         (rotated log from Jan 15)
pe.log.2024-01-14         (rotated log from Jan 14)
```

---

### AC4: Recovery Suggestions in User Messages

**Given** error occurs and displayed to user
**When** providing recovery suggestions
**Then** system shows:

```
❌ An Error Occurred

Diagnostic information saved to:
~/.prompt-enhancement/logs/pe.log

Suggested steps:
1. Check logs for detailed information
2. [Error-specific recovery steps]
3. Retry the operation
4. If issue persists, report the issue

For more help: /pe-help
```

**Error-Specific Recovery Steps:**
- **API_KEY_MISSING**: "Run /pe-setup to configure API key"
- **PROJECT_NOT_DETECTED**: "Ensure you're in project root with package.json or requirements.txt"
- **DETECTION_FAILED**: "Use --override to manually set standards or create .pe.yaml"
- **API_TIMEOUT**: "Check internet connection and retry"
- **PERMISSION_DENIED**: "Check file permissions or run from accessible directory"

---

### AC5: Log Viewer Command (`/pe-logs`)

**Given** user wants to view logs
**When** using `/pe-logs` command
**Then** system displays:
- Recent log entries (last 50 entries by default)
- Filtering options:
  - By level: `/pe-logs --level ERROR`
  - By date: `/pe-logs --date 2024-01-15`
  - By keyword: `/pe-logs --search "timeout"`
- Shows log file location
- Shows log rotation status (current size, days retained)

**Example Output:**
```
📋 Recent Logs (last 10 entries)

2024-01-15 14:30:45 | ERROR    | PROJECT_NOT_DETECTED
2024-01-15 14:28:12 | WARNING  | DETECTION_FAILED (confidence: 45%)
2024-01-15 14:25:01 | INFO     | Enhancement completed successfully
2024-01-15 14:22:33 | DEBUG    | Loading project configuration

Log file: ~/.prompt-enhancement/logs/pe.log
Size: 2.3 MB
Retention: 7 days (6 files)
```

---

### AC6: Sensitive Data Protection

**Given** sensitive information potentially in logs
**When** logging information
**Then** system:
- Never logs API keys (redact with `[REDACTED]`)
- Never logs user prompts (skip entirely)
- Never logs enhancement results (skip entirely)
- Never logs file contents (metadata only)
- Only logs metadata and error information

**Sensitive Fields to Redact:**
- `OPENAI_API_KEY`, `DEEPSEEK_API_KEY` → `[REDACTED]`
- `bearer_token`, `authorization` → `[REDACTED]`
- Environment variables containing "key", "token", "secret" → `[REDACTED]`

---

## Technical Requirements

### Logger Setup

```python
import logging
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("prompt_enhancement")

# Daily rotation at midnight
class MidnightRotatingFileHandler(RotatingFileHandler):
    """Custom handler for daily rotation at midnight."""
    pass
```

### Error Logging Wrapper

```python
@dataclass
class ErrorLog:
    timestamp: str  # ISO 8601
    level: str      # DEBUG, INFO, WARNING, ERROR
    category: str   # ErrorCategory enum
    message: str
    context: str
    project_fingerprint: str
    stack_trace: Optional[str]  # Only in DEBUG

    def to_json(self) -> str:
        """Convert to JSON for logging."""
```

### Recovery Information

```python
RECOVERY_SUGGESTIONS = {
    ErrorCategory.API_KEY_MISSING: [
        "Run /pe-setup to configure API key",
        "Or export OPENAI_API_KEY=sk-...",
        "Or add to ~/.prompt-enhancement/config.yaml"
    ],
    # ... etc for other categories
}
```

### Project Fingerprint Generation

```python
def generate_project_fingerprint(project_path: Path) -> str:
    """
    Generate stable, anonymized fingerprint from project characteristics.
    Example: prj_abc123
    """
```

---

## Testing Strategy

### Unit Tests

- **test_error_log_includes_all_fields**: Verify complete metadata
- **test_stack_trace_in_debug_only**: Verify no traces in production
- **test_no_api_keys_logged**: Verify API key redaction
- **test_no_prompts_logged**: Verify prompts excluded
- **test_log_level_filtering**: Verify DEBUG/INFO/WARNING/ERROR levels
- **test_log_file_created**: Verify ~/.prompt-enhancement/logs/pe.log
- **test_log_rotation_on_size**: Verify 10MB rotation
- **test_log_rotation_on_date**: Verify daily rotation
- **test_log_retention_7_days**: Verify old logs deleted
- **test_recovery_suggestions_shown**: Verify error-specific help
- **test_log_viewer_filters**: Verify /pe-logs filtering works

### Integration Tests

- **test_full_error_to_recovery_workflow**: End-to-end error handling
- **test_sensitive_data_never_logged**: Comprehensive data protection
- **test_log_rotation_under_load**: Multiple logs in succession

---

## Definition of Done

- [ ] Logger configuration implemented
- [ ] ErrorLog dataclass created
- [ ] Error classification to logging
- [ ] ISO 8601 timestamp formatting
- [ ] Project fingerprint generation
- [ ] Log level configuration working (DEBUG/INFO/WARNING/ERROR)
- [ ] Rotating file handler with 10MB + daily rotation
- [ ] 7-day retention implemented
- [ ] API key redaction working
- [ ] Prompt/result exclusion working
- [ ] Recovery suggestions added for all 5 error categories
- [ ] /pe-logs command implemented with filtering
- [ ] All 6 AC implemented and tested
- [ ] 11+ unit tests all passing
- [ ] Code review approved
- [ ] Story file updated to DONE

