# Changelog

All notable changes to the rich-logging module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Task Context Identification for Parallel Execution

- **New Module**: `rich_logging.core.log_context` - Thread-local storage for task context
  - `set_task_context(step_id: str, task_name: str, **extra_context)` - Set task context for current thread
  - `get_task_context() -> dict | None` - Get task context for current thread
  - `clear_task_context()` - Clear task context for current thread
  - Thread-safe using `threading.local()`

- **New Module**: `rich_logging.filters.task_context_filter` - Logging filter for task identification
  - `TaskContextFilter` class that automatically prepends task identifiers to log messages
  - Configurable format template (default: `"[{task_name}] "`)
  - Configurable styling with Rich markup support
  - Automatically checks thread-local storage for task context

- **RichLogger Enhancements**: Added task context management methods
  - `set_task_context(step_id: str, task_name: str, **extra_context)` - Set task context
  - `clear_task_context()` - Clear task context
  - `task_context(step_id: str, task_name: str, **extra_context)` - Context manager for automatic cleanup
  
  Example usage:
  ```python
  # Manual context management
  logger.set_task_context("install_nodejs", "Install Node.js")
  logger.info("Installing...")
  logger.clear_task_context()
  
  # Context manager (automatic cleanup)
  with logger.task_context("install_nodejs", "Install Node.js"):
      logger.info("Installing...")
  ```

- **RichHandlerSettings**: New configuration options
  - `show_task_context: bool = True` - Enable/disable task context display
  - `task_context_format: str = "[{task_name}] "` - Format template for task identifiers
  - `task_context_style: str = "cyan"` - Rich style for task context (color/formatting)
  
  Available format placeholders:
  - `{step_id}` - The step identifier (e.g., "install_nodejs")
  - `{task_name}` - Human-readable task name (e.g., "Install Node.js")

- **Console Handler**: Automatic filter attachment
  - `TaskContextFilter` is automatically attached to `RichHandler` when `show_task_context=True`
  - No manual configuration needed for basic usage

### Changed

- **RichHandler**: Now automatically includes task context in log messages during parallel execution
  - Log messages are prefixed with task identifiers when task context is set
  - Example output: `[install_nodejs] INFO     Installing Node.js...`

### Technical Details

**Problem Solved**: When executing tasks in parallel, log output from different tasks was interleaved and difficult to distinguish. This feature automatically adds task identifiers to log messages, making it easy to identify which parallel task produced which log line.

**Architecture**:
1. Thread-local storage (`LogContext`) tracks task context per thread
2. Logging filter (`TaskContextFilter`) checks context and prepends identifiers
3. Automatic integration with parallel execution (see pipeline module changelog)

**Thread Safety**: All components use `threading.local()` for thread-safe operation.

**Performance**: Minimal overhead - only a thread-local lookup per log message.

**Backward Compatibility**: Fully backward compatible. Existing code works without changes. Task context is optional and only appears when explicitly set.

### Documentation

- See `../PARALLEL_TASK_CONTEXT.md` for complete usage guide
- See `../IMPLEMENTATION_SUMMARY.md` for technical implementation details
- See `tests/test_task_context.py` for examples and test cases

### Migration Guide

**No migration needed** - This is a backward compatible feature addition.

To use the new task context feature:

```python
from rich_logging import Log, LogConfig
from rich_logging.handlers.rich_settings import RichHandlerSettings

# Create logger with task context enabled (default)
logger = Log.create_logger(
    config=LogConfig(
        name="my-logger",
        handler_config=RichHandlerSettings(
            show_task_context=True,  # Enabled by default
            task_context_format="[{task_name}] ",
            task_context_style="cyan",
        ),
    )
)

# Use in parallel execution
import threading

def worker(task_name):
    logger.set_task_context(f"task_{task_name}", task_name)
    logger.info("Working...")
    logger.clear_task_context()

threads = [
    threading.Thread(target=worker, args=("A",)),
    threading.Thread(target=worker, args=("B",)),
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

Output:
```
[A] INFO     Working...
[B] INFO     Working...
```

### API Additions Summary

**New Public APIs**:
- `rich_logging.core.log_context.set_task_context()`
- `rich_logging.core.log_context.get_task_context()`
- `rich_logging.core.log_context.clear_task_context()`
- `rich_logging.filters.task_context_filter.TaskContextFilter`
- `RichLogger.set_task_context()`
- `RichLogger.clear_task_context()`
- `RichLogger.task_context()` (context manager)

**New Configuration Options**:
- `RichHandlerSettings.show_task_context`
- `RichHandlerSettings.task_context_format`
- `RichHandlerSettings.task_context_style`

## [0.1.0] - Initial Release

- Initial release of rich-logging module
- Rich integration for enhanced console output
- Configurable logging handlers and formatters
- Support for multiple log levels and formats

