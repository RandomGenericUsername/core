# Rich Logging

Comprehensive Python logging library with Rich console integration. Enhances standard Python logging with beautiful console output, progress bars, tables, panels, and more.

## Features

- 🎨 **Rich Console Output**: Beautiful tables, panels, syntax highlighting, and more
- 📝 **Standard Logging Compatible**: Full compatibility with Python's `logging` module
- 🎯 **Simple API**: Clean, intuitive interface via `Log.create_logger()`
- 🔧 **Type-Safe Configuration**: Extensive use of type hints and dataclasses
- 📊 **Progress Tracking**: Built-in progress bars and status spinners
- 🔄 **Task Context**: Thread-safe context for parallel execution
- 💬 **Interactive Methods**: Rich prompts and confirmations
- 📁 **File Logging**: Support for file, rotating, and timed rotating handlers
- 🎭 **Graceful Degradation**: All Rich features degrade gracefully when unavailable
- ✅ **Fully Tested**: 140 passing tests with comprehensive coverage

## Installation

This module is used as a path dependency within the dotfiles project:

```toml
[project]
dependencies = [
    "rich-logging @ file://../../common/modules/logging",
]
```

## Quick Start

### Basic Logging

```python
from rich_logging import Log, LogLevels

# Create a logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Standard logging
logger.info("Application started")
logger.warning("This is a warning")
logger.error("An error occurred")
```

### Rich Console Features

```python
from rich_logging import Log, LogLevels, ConsoleHandlers, RichFeatureSettings

# Enable Rich features
logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    console_handler_type=ConsoleHandlers.RICH,
    rich_features=RichFeatureSettings(enabled=True)
)

# Display a panel
logger.panel("Important Message", title="Alert", border_style="red")

# Display a table
data = [
    ["Name", "Age"],
    ["Alice", "30"],
    ["Bob", "25"]
]
logger.table(data, show_header=True)

# Syntax highlighting
code = 'def hello():\n    print("Hello!")'
logger.syntax(code, "python")
```

### Progress Tracking

```python
import time

with logger.progress() as progress:
    task = progress.add_task("Processing", total=100)

    for i in range(100):
        # Do work
        time.sleep(0.01)
        progress.update(task, advance=1)
```

### Task Context for Parallel Execution

```python
import concurrent.futures

def process_item(item_id):
    with logger.task_context(f"item_{item_id}"):
        logger.info(f"Processing item {item_id}")
        # Do work

with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    executor.map(process_item, range(10))
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Usage Guide](docs/usage-guide.md)** - Getting started, common workflows, and best practices
- **[API Reference](docs/api-reference.md)** - Complete API documentation with examples
- **[Configuration Reference](docs/configuration.md)** - All configuration options and settings
- **[Advanced Features](docs/advanced-features.md)** - Rich display methods, context managers, and interactive features
- **[Architecture](docs/architecture.md)** - System design, patterns, and extension points

All documentation is grounded in verified behavior from our comprehensive test suite (140 passing tests).

## Examples

### Multiple Loggers

```python
# Create separate loggers for different components
api_logger = Log.create_logger("api", log_level=LogLevels.DEBUG)
db_logger = Log.create_logger("database", log_level=LogLevels.INFO)

api_logger.debug("API request received")
db_logger.info("Database query executed")
```

### Update Logger Configuration

```python
# Create logger
logger = Log.create_logger("myapp", log_level=LogLevels.INFO)

# Later, update configuration
logger = Log.update("myapp", log_level=LogLevels.DEBUG)
```

### Custom Formatters

```python
from rich_logging import LogFormatters, LogFormatterStyleChoices

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    formatter_type=LogFormatters.COLORED,
    formatter_style=LogFormatterStyleChoices.BRACE,
    format="{asctime} | {levelname} | {message}"
)
```

### File Logging

```python
from rich_logging import FileHandlerSpec, FileHandlerTypes, FileHandlerSettings

file_spec = FileHandlerSpec(
    handler_type=FileHandlerTypes.ROTATING_FILE,
    config=RotatingFileHandlerSettings(
        filename="app.log",
        maxBytes=10_000_000,  # 10 MB
        backupCount=5
    )
)

logger = Log.create_logger(
    "myapp",
    log_level=LogLevels.INFO,
    file_handlers=[file_spec]
)
```

## Development

### Setup

```bash
# Install dependencies
uv sync

# Run tests
uv run pytest tests/

# Run specific test categories
uv run pytest tests/contract/      # Contract tests
uv run pytest tests/integration/   # Integration tests
uv run pytest tests/unit/          # Unit tests
```

### Testing

The project follows a tests-first documentation approach with comprehensive test coverage:

- **140 passing tests** across contract, integration, and unit test categories
- All documentation claims are backed by test evidence
- Tests verify both standard logging and Rich features
- Graceful degradation is tested for all Rich features

```bash
# Run all tests with verbose output
uv run pytest tests/ -v

# Run tests with coverage
uv run pytest tests/ --cov=rich_logging --cov-report=html
```

### Code Quality

```bash
# Format code
uv run black .
uv run isort .

# Type check
uv run mypy .

# Lint
uv run ruff check .
```

## Requirements

- **Python 3.12+**
- **Rich >=13.0.0**

## Project Structure

```
rich-logging/
├── src/rich_logging/          # Source code
│   ├── core/                  # Core types and utilities
│   ├── formatters/            # Log formatters
│   ├── handlers/              # Log handlers
│   ├── filters/               # Log filters
│   ├── rich/                  # Rich features
│   └── log.py                 # Main API
├── tests/                     # Test suite (140 tests)
│   ├── contract/              # API contract tests
│   ├── integration/           # End-to-end tests
│   └── unit/                  # Component tests
└── docs/                      # Documentation
    ├── usage-guide.md
    ├── api-reference.md
    ├── configuration.md
    ├── advanced-features.md
    └── architecture.md
```

## Contributing

This is a personal dotfiles module, but suggestions and bug reports are welcome.

## License

MIT
