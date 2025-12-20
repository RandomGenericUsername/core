# Changelog

All notable changes to the task-pipeline module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### Automatic Task Context for Parallel Execution

- **ParallelTaskExecutor Enhancement**: Automatic task context management
  - New private method `_execute_with_context()` wraps parallel task execution
  - Automatically sets task context before executing each parallel step
  - Automatically clears task context after execution (with try/finally for safety)
  - Uses step's `step_id` and `description` for task identification
  - Integrates with rich-logging module's task context feature

- **ParallelConfig**: New configuration options
  - `show_task_identifiers: bool = True` - Enable/disable task identifiers in log output
  - `use_visual_separators: bool = False` - Enable visual separators for parallel tasks (reserved for future use)

### Changed

- **ParallelTaskExecutor.execute()**: Now uses `_execute_with_context()` wrapper
  - Each parallel task automatically gets task context set
  - Log messages from parallel tasks are automatically prefixed with task identifiers
  - Example: `[install_nodejs] INFO     Installing Node.js...`
  - No changes needed in individual pipeline steps

### Technical Details

**Problem Solved**: When executing tasks in parallel, log output from different tasks was interleaved and difficult to distinguish. This enhancement automatically adds task identifiers to log messages during parallel execution.

**How It Works**:
1. `ParallelTaskExecutor` submits tasks to `ThreadPoolExecutor`
2. Each task is wrapped with `_execute_with_context()`
3. Before execution: `logger.set_task_context(step_id, description)`
4. Task executes normally
5. After execution: `logger.clear_task_context()` (in finally block)
6. The rich-logging module's `TaskContextFilter` automatically prepends task identifiers to log messages

**Thread Safety**: Uses thread-local storage from rich-logging module. Each parallel task has independent context.

**Performance**: Minimal overhead - only setting/clearing thread-local storage per task.

**Backward Compatibility**: Fully backward compatible. Existing pipeline steps work without any changes.

### Integration with rich-logging

This feature requires rich-logging >= 0.2.0 (unreleased) which includes:
- `LogContext` for thread-local task context storage
- `TaskContextFilter` for automatic task identifier prefixing
- `RichLogger.set_task_context()` and `clear_task_context()` methods

See rich-logging CHANGELOG.md for details.

### Documentation

- See `../PARALLEL_TASK_CONTEXT.md` for complete usage guide
- See `../IMPLEMENTATION_SUMMARY.md` for technical implementation details

### Migration Guide

**No migration needed** - This is a backward compatible feature addition.

The feature works automatically when using parallel execution:

```python
from task_pipeline import Pipeline, PipelineContext, PipelineStep
from task_pipeline.core.types import ParallelConfig

# Define pipeline with parallel steps
steps = [
    [  # Parallel group - these run concurrently
        InstallNodeJsStep(),
        InstallPythonStep(),
        InstallRustStep(),
    ]
]

# Create pipeline (task context is automatic)
pipeline = Pipeline(steps=steps)
result = pipeline.run(context)
```

Output automatically includes task identifiers:
```
[Install Node.js] INFO     Starting installation...
[Install Python]  INFO     Starting installation...
[Install Rust]    INFO     Starting installation...
[Install Node.js] INFO     ✓ Installation complete!
[Install Python]  INFO     ✓ Installation complete!
[Install Rust]    INFO     ✓ Installation complete!
```

To disable task identifiers (if needed):

```python
from task_pipeline.core.types import ParallelConfig

# Configure parallel execution
config = ParallelConfig(
    show_task_identifiers=False,  # Disable task identifiers
)

# Note: Currently this config option is defined but not yet wired up
# to disable the feature. It's reserved for future use.
# To disable, configure the logger's RichHandlerSettings instead:
# RichHandlerSettings(show_task_context=False)
```

### Example: Before and After

**Before this change:**
```
INFO     Installing rust...
INFO     Installing nodejs...
INFO     python is already installed
ERROR    Failed to install nodejs
```
(Hard to tell which task failed!)

**After this change:**
```
[install_rust]   INFO     Installing rust...
[install_nodejs] INFO     Installing nodejs...
[install_python] INFO     python is already installed
[install_nodejs] ERROR    Failed to install nodejs
```
(Clear which task produced each log line!)

### API Changes Summary

**New Public APIs**:
- `ParallelConfig.show_task_identifiers` (configuration option)
- `ParallelConfig.use_visual_separators` (configuration option, reserved)

**New Private APIs**:
- `ParallelTaskExecutor._execute_with_context()` (internal wrapper method)

**Modified Behavior**:
- `ParallelTaskExecutor.execute()` now automatically sets task context for each parallel task
- Log messages from parallel tasks are automatically prefixed with task identifiers

**No Breaking Changes**: All existing code continues to work without modification.

### Dependencies

- Requires `rich-logging >= 0.2.0` (unreleased) for task context functionality
- Update your dependencies when rich-logging 0.2.0 is released

## [0.1.0] - Initial Release

- Initial release of task-pipeline module
- Support for serial and parallel task execution
- Pipeline progress tracking
- Context merging for parallel execution
- Flexible step configuration

