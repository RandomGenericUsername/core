# dotfiles-package-manager

A unified abstraction layer for Linux package managers, providing a consistent interface across Arch, Debian, and RedHat-based distributions.

**Version:** 0.2.0 | **Python:** 3.12+ | **Status:** ✅ All 189 tests passing

## Quick Start

This project provides a single API to manage packages across different Linux distributions:

```python
from dotfiles_package_manager import PackageManagerFactory

# Automatically detect the system's package manager
pm = PackageManagerFactory.create()

# Use the same API regardless of the underlying manager
result = pm.install(["package1", "package2"])
if result.success:
    print(f"Installed successfully: {result.packages}")
```

## Supported Package Managers

| Distribution | Package Managers |
|---|---|
| Arch Linux | `pacman`, `yay`, `paru` |
| Debian/Ubuntu | `apt` |
| Fedora/RHEL | `dnf` |

## Documentation

For comprehensive documentation, guides, and API reference, see the [`docs/`](docs/README.md) directory:

| Topic | Link | Best For |
|---|---|---|
| **Getting Started** | [Quick Start Guide](docs/guides/QuickStart.md) | First-time users |
| **Full Documentation** | [Documentation Index](docs/README.md) | Complete reference |
| **API Reference** | [API Docs](docs/api/) | Integration details |
| **Architecture** | [System Design](docs/architecture/Overview.md) | Contributors |
| **Advanced Usage** | [Advanced Guide](docs/guides/AdvancedUsage.md) | Feature exploration |

## Documentation Structure

```
docs/
├── README.md                          # Main documentation index
├── guides/                            # User guides
│   ├── QuickStart.md                  # Get started in 5 minutes
│   ├── AdvancedUsage.md               # All features with examples
│   └── ErrorHandling.md               # Exception patterns
├── api/                               # API reference
│   ├── PackageManager.md              # Core abstract class
│   ├── PackageManagerFactory.md       # Factory for creating managers
│   └── Types.md                       # Enums, data classes, exceptions
├── architecture/                      # Design documentation
│   ├── Overview.md                    # System design and patterns
│   └── ImplementationGuide.md         # Adding new package managers
└── reference/                         # Behavior specifications
    ├── PartialFailures.md             # Handling partial successes
    ├── EmptyLists.md                  # Empty package list behavior
    └── ExceptionPropagation.md        # Exception handling details
```

## Key Features

- **Unified API** - Single interface across 5 different package managers
- **Type-Safe** - Full type hints with mypy strict mode compliance
- **Well-Tested** - 189 contract and characterization tests
- **Exception Safe** - Consistent error handling across all managers
- **Zero Dependencies** - No external dependencies for the core library

## Development

### Running Tests

```bash
# Install development dependencies
uv sync --extra dev

# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=src/dotfiles_package_manager

# Run specific test categories
uv run pytest tests/contract/ -v          # Cross-manager consistency tests
uv run pytest tests/characterization/ -v  # Behavior specification tests
```

### Code Quality

```bash
# Format code
uv run black src/ tests/

# Lint with ruff
uv run ruff check src/ tests/

# Type check
uv run mypy src/

# Run isort
uv run isort src/ tests/
```

## Project Structure

```
src/dotfiles_package_manager/
├── core/
│   ├── base.py          # Abstract PackageManager class
│   ├── types.py         # Types, enums, and exceptions
│   └── factory.py       # PackageManagerFactory implementation
├── implementations/
│   ├── arch/            # Arch Linux package managers
│   ├── debian/          # Debian/Ubuntu package manager
│   └── redhat/          # Fedora/RHEL package manager
└── __init__.py          # Public API exports
```

## Contributing

For guidelines on adding new package managers or extending functionality, see [Implementation Guide](docs/architecture/ImplementationGuide.md).

## Documentation Standards

This project follows **Tests-First Documentation** principles:

- All behavior claims are backed by test evidence
- No speculation - unknowns are explicitly marked
- Public contracts documented before implementation details
- Cross-manager consistency verified by automated tests

See [docs/README.md](docs/README.md) for full documentation and evidence tables.

## License

[Add your license information here]
