# Parallel Task Context Identification

## Overview

When executing tasks in parallel using the pipeline module, log output from different tasks can become interleaved and difficult to distinguish. This feature automatically adds task identifiers to log messages, making it easy to identify which parallel task produced which log line.

## Problem Solved

**Before:**
```
INFO     oh-my-zsh is already installed                       base.py:76
DEBUG    Version: [ -n "$ZSH_VERSION" ] || {                  base.py:79
WARNING  Feature pyenv not found in configuration    feature_steps.py:57
INFO     Installing rust...                                   base.py:82
INFO     Installing nodejs...                                 base.py:82
```

**After:**
```
[install_oh_my_zsh] INFO     oh-my-zsh is already installed                       base.py:76
[install_oh_my_zsh] DEBUG    Version: [ -n "$ZSH_VERSION" ] || {                  base.py:79
[install_pyenv]     WARNING  Feature pyenv not found in configuration    feature_steps.py:57
[install_rust]      INFO     Installing rust...                                   base.py:82
[install_nodejs]    INFO     Installing nodejs...                                 base.py:82
```

## How It Works

### Architecture

1. **Thread-Local Storage**: Each thread stores its task context independently using `threading.local()`
2. **Automatic Context Injection**: The `ParallelTaskExecutor` automatically sets/clears task context
3. **Logging Filter**: A `TaskContextFilter` prepends task identifiers to log messages
4. **Zero Configuration**: Works automatically with existing code - no changes needed in individual steps

### Components

#### 1. LogContext (logging/src/rich_logging/core/log_context.py)
Thread-local storage for task context:
```python
from rich_logging.core.log_context import set_task_context, clear_task_context

# Set context for current thread
set_task_context("install_nodejs", "Install Node.js")

# Clear context when done
clear_task_context()
```

#### 2. TaskContextFilter (logging/src/rich_logging/filters/task_context_filter.py)
Logging filter that adds task identifiers to messages:
```python
from rich_logging.filters.task_context_filter import TaskContextFilter

filter = TaskContextFilter(
    enabled=True,
    format_template="[{task_name}] ",
    task_style="cyan"
)
handler.addFilter(filter)
```

#### 3. RichLogger Enhancement (logging/src/rich_logging/rich/rich_logger.py)
Added methods for task context management:
```python
# Set task context
logger.set_task_context("install_nodejs", "Install Node.js")

# Use context manager (automatic cleanup)
with logger.task_context("install_nodejs", "Install Node.js"):
    logger.info("Installing...")
    # Context automatically cleared after block
```

#### 4. ParallelTaskExecutor Integration (pipeline/src/task_pipeline/executors/parallel_executor.py)
Automatically sets/clears context for each parallel task:
- Sets context before executing each step
- Clears context after execution (even if exception occurs)
- Uses step_id and description for identification

## Configuration

### Logging Configuration

Configure task context display in `RichHandlerSettings`:

```python
from rich_logging.handlers.rich_settings import RichHandlerSettings

settings = RichHandlerSettings(
    show_task_context=True,              # Enable/disable task context
    task_context_format="[{task_name}] ", # Format template
    task_context_style="cyan",            # Rich style (color)
)
```

### Pipeline Configuration

Configure parallel execution behavior in `ParallelConfig`:

```python
from task_pipeline.core.types import ParallelConfig

config = ParallelConfig(
    show_task_identifiers=True,    # Enable task identifiers (default: True)
    use_visual_separators=False,   # Add visual separators (default: False)
)
```

## Usage Examples

### Example 1: Basic Usage (Automatic)

No code changes needed! Task context is automatically added when using parallel execution:

```python
from task_pipeline import Pipeline, PipelineContext

steps = [
    [  # Parallel group
        InstallNodeJsStep(),
        InstallPythonStep(),
        InstallRustStep(),
    ]
]

pipeline = Pipeline(steps=steps)
result = pipeline.run(context)
# Log output automatically includes task identifiers
```

### Example 2: Manual Context Management

For custom parallel execution outside the pipeline:

```python
import threading
from rich_logging.core.log_context import set_task_context, clear_task_context

def install_package(package_name, logger):
    set_task_context(f"install_{package_name}", f"Install {package_name}")
    try:
        logger.info(f"Installing {package_name}...")
        # ... installation logic ...
    finally:
        clear_task_context()

# Run in parallel
threads = [
    threading.Thread(target=install_package, args=("nodejs", logger)),
    threading.Thread(target=install_package, args=("python", logger)),
]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

### Example 3: Context Manager

Use the context manager for automatic cleanup:

```python
with logger.task_context("install_nodejs", "Install Node.js"):
    logger.info("Starting installation...")
    logger.debug("Checking dependencies...")
    logger.info("Installation complete!")
# Context automatically cleared
```

## Customization

### Custom Format Templates

Available placeholders:
- `{step_id}`: The step identifier (e.g., "install_nodejs")
- `{task_name}`: Human-readable task name (e.g., "Install Node.js")

Examples:
```python
task_context_format="[{step_id}] "           # [install_nodejs]
task_context_format="({task_name}) "         # (Install Node.js)
task_context_format="{task_name}: "          # Install Node.js:
task_context_format="[{step_id}|{task_name}] "  # [install_nodejs|Install Node.js]
```

### Custom Styles

Use any Rich style string:
```python
task_context_style="cyan"           # Cyan text
task_context_style="bold blue"      # Bold blue text
task_context_style="dim"            # Dimmed text
task_context_style="bold green"     # Bold green text
```

## Testing

Run the test suite to verify functionality:

```bash
cd v2.0/dotfiles-core/logging
python tests/test_task_context.py
```

## Benefits

1. **Clear Identification**: Every log line shows which task it belongs to
2. **Easy Debugging**: Can filter/search logs by task identifier
3. **No Performance Impact**: Minimal overhead from thread-local storage
4. **Backward Compatible**: Works with existing code, no changes to steps needed
5. **Thread-Safe**: Uses proper thread-local storage
6. **Configurable**: Can disable or customize the format

## Implementation Details

- Thread-local storage ensures each thread has independent context
- Filter is attached to handlers during logger creation
- Context is automatically set/cleared by ParallelTaskExecutor
- Works with both RichHandler and standard StreamHandler
- No changes needed in individual pipeline steps

