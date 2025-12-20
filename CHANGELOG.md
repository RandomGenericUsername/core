# Changelog - dotfiles-core

All notable changes to the dotfiles-core project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Parallel Task Context Identification

A new feature that automatically adds task identifiers to log messages during parallel execution, solving the problem of mixed/interleaved output from concurrent tasks.

#### Overview

**Problem**: When executing tasks in parallel, log output from different tasks was interleaved and difficult to distinguish.

**Solution**: Automatic task context identification using thread-local storage and logging filters.

**Result**: Log messages are now prefixed with task identifiers (e.g., `[install_nodejs] INFO Installing...`)

#### Modules Updated

##### rich-logging (0.1.0 → 0.2.0)

**New Features**:
- Thread-local task context storage (`rich_logging.core.log_context`)
- Task context logging filter (`rich_logging.filters.task_context_filter`)
- Task context methods on `RichLogger`: `set_task_context()`, `clear_task_context()`, `task_context()`
- Configuration options in `RichHandlerSettings`: `show_task_context`, `task_context_format`, `task_context_style`

**API Additions**:
```python
# Set task context for current thread
logger.set_task_context("install_nodejs", "Install Node.js")

# Use context manager (automatic cleanup)
with logger.task_context("install_nodejs", "Install Node.js"):
    logger.info("Installing...")

# Clear task context
logger.clear_task_context()
```

See `logging/CHANGELOG.md` for complete details.

##### task-pipeline (0.1.0 → 0.2.0)

**New Features**:
- Automatic task context management in `ParallelTaskExecutor`
- Configuration options in `ParallelConfig`: `show_task_identifiers`, `use_visual_separators`

**Behavior Changes**:
- Parallel tasks automatically get task context set/cleared
- Log messages from parallel tasks are automatically prefixed with task identifiers
- No changes needed in individual pipeline steps

See `pipeline/CHANGELOG.md` for complete details.

#### Usage Example

```python
from task_pipeline import Pipeline, PipelineContext

# Define pipeline with parallel steps
steps = [
    [  # Parallel group
        InstallNodeJsStep(),
        InstallPythonStep(),
        InstallRustStep(),
    ]
]

# Run pipeline - task context is automatic!
pipeline = Pipeline(steps=steps)
result = pipeline.run(context)
```

**Output**:
```
[Install Node.js] INFO     Starting installation...
[Install Python]  INFO     Starting installation...
[Install Rust]    INFO     Starting installation...
[Install Node.js] INFO     ✓ Installation complete!
[Install Python]  INFO     ✓ Installation complete!
[Install Rust]    INFO     ✓ Installation complete!
```

#### Configuration

**Enable/Disable** (enabled by default):
```python
from rich_logging.handlers.rich_settings import RichHandlerSettings

settings = RichHandlerSettings(
    show_task_context=True,  # Set to False to disable
)
```

**Customize Format**:
```python
settings = RichHandlerSettings(
    task_context_format="({task_name}) ",  # Use parentheses
    task_context_style="bold blue",        # Change color
)
```

#### Documentation

- **`PARALLEL_TASK_CONTEXT.md`** - Complete usage guide with examples
- **`IMPLEMENTATION_SUMMARY.md`** - Technical implementation details
- **`logging/CHANGELOG.md`** - Detailed logging module changes
- **`pipeline/CHANGELOG.md`** - Detailed pipeline module changes

#### Migration Guide

**No migration needed** - This is a fully backward compatible feature addition.

- Existing code works without any changes
- Task context is automatically added during parallel execution
- Can be disabled via configuration if needed

#### Testing

Run the test suite:
```bash
cd logging
python tests/test_task_context.py
```

All tests pass ✓

#### Benefits

1. ✅ **Clear Identification**: Every log line shows which task it belongs to
2. ✅ **Zero Configuration**: Works automatically with existing code
3. ✅ **Thread-Safe**: Uses proper thread-local storage
4. ✅ **Configurable**: Can customize format and styling
5. ✅ **Backward Compatible**: No changes needed in existing steps
6. ✅ **Minimal Overhead**: Negligible performance impact

#### Files Changed

**Created**:
- `logging/src/rich_logging/core/log_context.py`
- `logging/src/rich_logging/filters/__init__.py`
- `logging/src/rich_logging/filters/task_context_filter.py`
- `logging/tests/test_task_context.py`
- `PARALLEL_TASK_CONTEXT.md`
- `IMPLEMENTATION_SUMMARY.md`
- `logging/CHANGELOG.md`
- `pipeline/CHANGELOG.md`
- `CHANGELOG.md` (this file)

**Modified**:
- `logging/src/rich_logging/handlers/rich_settings.py`
- `logging/src/rich_logging/handlers/console.py`
- `logging/src/rich_logging/rich/rich_logger.py`
- `pipeline/src/task_pipeline/executors/parallel_executor.py`
- `pipeline/src/task_pipeline/core/types.py`

## [0.1.0] - Initial Release

Initial release of dotfiles-core project containing:
- **rich-logging** (0.1.0) - Comprehensive logging with Rich integration
- **task-pipeline** (0.1.0) - Flexible pipeline execution framework

