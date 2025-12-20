#!/usr/bin/env python3
"""Demo showing task context identification in parallel execution.

This demo demonstrates how task identifiers are automatically added to log
messages when executing parallel tasks, making it easy to identify which
task produced which log line.
"""

import sys
import time
from pathlib import Path
from typing import Any

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from task_pipeline import Pipeline, PipelineContext, PipelineStep

# Import logging modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "logging" / "src"))

from rich_logging import Log, LogConfig
from rich_logging.core.log_types import ConsoleHandlers, LogFormatters, LogFormatterStyleChoices
from rich_logging.handlers.rich_settings import RichHandlerSettings
from rich_logging.rich.rich_feature_settings import RichFeatureSettings


class MockConfig:
    """Mock config for demo."""
    pass


class ParallelInstallStep(PipelineStep):
    """Step that simulates installing a package with logging."""

    def __init__(self, step_id_val: str, package_name: str, duration: float):
        self._step_id = step_id_val
        self.package_name = package_name
        self.duration = duration

    @property
    def step_id(self) -> str:
        return self._step_id

    @property
    def description(self) -> str:
        return f"Install {self.package_name}"

    def run(self, context: PipelineContext[Any]) -> PipelineContext[Any]:
        logger = context.logger_instance
        
        # Simulate installation steps with logging
        logger.info(f"Starting {self.package_name} installation...")
        time.sleep(self.duration * 0.2)
        
        logger.debug(f"Checking if {self.package_name} is already installed")
        time.sleep(self.duration * 0.2)
        
        logger.info(f"Downloading {self.package_name}...")
        time.sleep(self.duration * 0.3)
        
        logger.info(f"Installing {self.package_name}...")
        time.sleep(self.duration * 0.2)
        
        logger.info(f"✓ {self.package_name} installed successfully!")
        time.sleep(self.duration * 0.1)
        
        context.results[f"{self._step_id}_installed"] = True
        return context


def main() -> None:
    """Run the demo."""
    print("=" * 80)
    print("PARALLEL EXECUTION WITH TASK CONTEXT IDENTIFICATION")
    print("=" * 80)
    print("\nThis demo shows how task identifiers are automatically added to")
    print("log messages during parallel execution, making it easy to identify")
    print("which task produced which log line.\n")
    
    # Create a logger with Rich features
    logger = Log.create_logger(
        config=LogConfig(
            name="demo-parallel",
            log_level="DEBUG",
            formatter_style=LogFormatterStyleChoices.BRACE,
            formatter_type=LogFormatters.RICH,
            console_handler=ConsoleHandlers.RICH,
            handler_config=RichHandlerSettings(
                show_time=True,
                show_path=False,
                markup=True,
                rich_tracebacks=True,
                # Task context is enabled by default
                show_task_context=True,
                task_context_format="[{task_name}] ",
                task_context_style="cyan",
            ),
            rich_features=RichFeatureSettings(
                enabled=True,
            ),
        )
    )
    
    # Create context
    context = PipelineContext(
        app_config=MockConfig(),
        logger_instance=logger,
    )
    
    # Define pipeline with parallel installation steps
    steps = [
        [  # Parallel group - these 4 steps run concurrently
            ParallelInstallStep("install_nodejs", "Node.js", duration=2.0),
            ParallelInstallStep("install_python", "Python", duration=1.5),
            ParallelInstallStep("install_rust", "Rust", duration=2.5),
            ParallelInstallStep("install_go", "Go", duration=1.8),
        ],
    ]
    
    print("=" * 80)
    print("EXECUTING PARALLEL INSTALLATIONS")
    print("=" * 80)
    print("\nNotice how each log line is prefixed with the task identifier")
    print("(e.g., [Install Node.js], [Install Python], etc.)\n")
    
    # Run pipeline
    pipeline = Pipeline(steps=steps)
    start_time = time.time()
    result = pipeline.run(context)
    elapsed = time.time() - start_time
    
    # Show results
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total Time: {elapsed:.2f}s")
    print(f"All installations completed: {all(result.results.values())}")
    print("\nInstalled packages:")
    for key, value in result.results.items():
        if key.endswith("_installed") and value:
            package = key.replace("install_", "").replace("_installed", "")
            print(f"  ✓ {package}")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()

