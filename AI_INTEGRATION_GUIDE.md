# AI Integration Guide - Parallel Task Context Feature

This guide is designed for AI tools that need to integrate with or update code that depends on dotfiles-core.

## Quick Summary

**What Changed**: Added automatic task identification for parallel execution in the pipeline module.

**Impact**: Log messages from parallel tasks are now automatically prefixed with task identifiers.

**Backward Compatibility**: ✅ Fully backward compatible - no code changes required.

**Version**: rich-logging 0.1.0 → 0.2.0, task-pipeline 0.1.0 → 0.2.0

## For AI Tools: What You Need to Know

### 1. No Breaking Changes

All existing code continues to work without modification. This is a feature addition, not a breaking change.

### 2. New Behavior (Automatic)

When using parallel execution in the pipeline, log output now includes task identifiers:

**Before**:
```
INFO     Installing nodejs...
INFO     Installing python...
```

**After**:
```
[install_nodejs] INFO     Installing nodejs...
[install_python] INFO     Installing python...
```

### 3. New APIs Available (Optional)

If you want to manually manage task context outside the pipeline:

```python
from rich_logging.core.log_context import set_task_context, clear_task_context

# Set context
set_task_context("task_id", "Task Name")

# Your code here
logger.info("This will be prefixed with [Task Name]")

# Clear context
clear_task_context()
```

Or use the context manager:

```python
with logger.task_context("task_id", "Task Name"):
    logger.info("This will be prefixed with [Task Name]")
# Context automatically cleared
```

### 4. Configuration (Optional)

To customize or disable the feature:

```python
from rich_logging.handlers.rich_settings import RichHandlerSettings

# Customize format
settings = RichHandlerSettings(
    show_task_context=True,              # Enable/disable
    task_context_format="[{task_name}] ", # Format template
    task_context_style="cyan",            # Color/style
)

# Use when creating logger
logger = Log.create_logger(
    config=LogConfig(
        name="my-logger",
        handler_config=settings,
    )
)
```

## For Dependent Projects

### If Your Project Uses task-pipeline

**Action Required**: None - feature works automatically

**Optional**: Update your code to take advantage of clearer log output in parallel execution

**Example**: If you have custom parallel execution logic, you can now use task context:

```python
import threading
from rich_logging.core.log_context import set_task_context, clear_task_context

def worker(task_id, task_name):
    set_task_context(task_id, task_name)
    try:
        # Your parallel work here
        logger.info("Working...")
    finally:
        clear_task_context()

threads = [
    threading.Thread(target=worker, args=("task1", "Task 1")),
    threading.Thread(target=worker, args=("task2", "Task 2")),
]
```

### If Your Project Uses rich-logging

**Action Required**: None - existing loggers continue to work

**Optional**: Enable task context if you have custom parallel execution:

```python
# When creating logger, task context is enabled by default
logger = Log.create_logger(config=LogConfig(name="my-logger"))

# Use in parallel code
with logger.task_context("my_task", "My Task"):
    logger.info("This gets prefixed with [My Task]")
```

## Common Integration Patterns

### Pattern 1: Using Pipeline with Parallel Steps (Automatic)

```python
from task_pipeline import Pipeline

steps = [
    [  # Parallel group
        MyStep1(),
        MyStep2(),
        MyStep3(),
    ]
]

pipeline = Pipeline(steps=steps)
result = pipeline.run(context)
# Task context is automatic - no changes needed!
```

### Pattern 2: Custom Parallel Execution

```python
import threading
from rich_logging.core.log_context import set_task_context, clear_task_context

def parallel_worker(task_id, task_name, logger):
    set_task_context(task_id, task_name)
    try:
        logger.info("Starting work...")
        # Do work
        logger.info("Work complete!")
    finally:
        clear_task_context()

threads = []
for i, task in enumerate(tasks):
    t = threading.Thread(
        target=parallel_worker,
        args=(f"task_{i}", task.name, logger)
    )
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### Pattern 3: Disabling Task Context

```python
from rich_logging import Log, LogConfig
from rich_logging.handlers.rich_settings import RichHandlerSettings

logger = Log.create_logger(
    config=LogConfig(
        name="my-logger",
        handler_config=RichHandlerSettings(
            show_task_context=False,  # Disable task context
        ),
    )
)
```

## Testing Your Integration

1. **Run existing tests** - They should all pass without changes
2. **Check parallel execution** - Log output should now include task identifiers
3. **Verify no regressions** - Serial execution should work exactly as before

## Troubleshooting

### Issue: Task identifiers not showing up

**Solution**: Ensure you're using rich-logging >= 0.2.0 and task-pipeline >= 0.2.0

### Issue: Want to disable task identifiers

**Solution**: Set `show_task_context=False` in `RichHandlerSettings`

### Issue: Want different format

**Solution**: Customize `task_context_format` and `task_context_style` in `RichHandlerSettings`

## References

- **CHANGELOG.md** - Complete changelog for all modules
- **PARALLEL_TASK_CONTEXT.md** - Detailed feature documentation
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **logging/CHANGELOG.md** - Logging module specific changes
- **pipeline/CHANGELOG.md** - Pipeline module specific changes

## Summary for AI Tools

**Key Points**:
1. ✅ Backward compatible - no code changes required
2. ✅ Automatic in pipeline parallel execution
3. ✅ Optional manual API for custom parallel code
4. ✅ Configurable format and styling
5. ✅ Can be disabled if needed

**Recommendation**: Update dependency versions and test. No code changes needed unless you want to use the new manual APIs.

