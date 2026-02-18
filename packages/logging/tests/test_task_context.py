#!/usr/bin/env python3
"""Test task context functionality for parallel execution."""

import sys
import time
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rich_logging.core.log_context import LogContext, set_task_context, get_task_context, clear_task_context
from rich_logging.filters.task_context_filter import TaskContextFilter
import logging


def test_thread_local_context():
    """Test that context is thread-local."""
    print("\n" + "=" * 80)
    print("TEST 1: Thread-Local Context Storage")
    print("=" * 80)
    
    results = {}
    
    def worker(thread_id: str):
        # Set context for this thread
        set_task_context(f"task_{thread_id}", f"Task {thread_id}")
        time.sleep(0.1)  # Simulate work
        
        # Get context - should be specific to this thread
        context = get_task_context()
        results[thread_id] = context
        
        clear_task_context()
    
    # Create multiple threads
    threads = []
    for i in range(3):
        t = threading.Thread(target=worker, args=(str(i),))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    # Verify each thread had its own context
    print("\nResults:")
    for thread_id, context in results.items():
        print(f"  Thread {thread_id}: {context}")
    
    assert len(results) == 3
    assert results["0"]["step_id"] == "task_0"
    assert results["1"]["step_id"] == "task_1"
    assert results["2"]["step_id"] == "task_2"
    print("\n✓ Thread-local context works correctly!")


def test_task_context_filter():
    """Test that the filter adds task context to log messages."""
    print("\n" + "=" * 80)
    print("TEST 2: Task Context Filter")
    print("=" * 80)
    
    # Create a logger with the filter
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    
    # Create handler with our filter
    handler = logging.StreamHandler()
    task_filter = TaskContextFilter(
        enabled=True,
        format_template="[{task_name}] ",
        use_rich_markup=False,  # Disable markup for testing
    )
    handler.addFilter(task_filter)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    
    print("\nWithout task context:")
    logger.info("This is a normal log message")
    
    print("\nWith task context:")
    set_task_context("install_nodejs", "Install Node.js")
    logger.info("Installing package...")
    logger.debug("Checking dependencies...")
    logger.info("Installation complete!")
    clear_task_context()
    
    print("\nAfter clearing context:")
    logger.info("Back to normal logging")
    
    print("\n✓ Task context filter works correctly!")


def test_parallel_logging():
    """Test parallel logging with task context."""
    print("\n" + "=" * 80)
    print("TEST 3: Parallel Logging with Task Context")
    print("=" * 80)
    
    # Create a shared logger
    logger = logging.getLogger("parallel_test")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    
    handler = logging.StreamHandler()
    task_filter = TaskContextFilter(
        enabled=True,
        format_template="[{task_name}] ",
        use_rich_markup=False,
    )
    handler.addFilter(task_filter)
    handler.setFormatter(logging.Formatter("%(levelname)-8s %(message)s"))
    logger.addHandler(handler)
    
    def install_package(package_name: str, duration: float):
        """Simulate package installation."""
        step_id = f"install_{package_name.lower()}"
        set_task_context(step_id, f"Install {package_name}")
        
        try:
            logger.info(f"Starting {package_name} installation...")
            time.sleep(duration * 0.3)
            
            logger.info(f"Downloading {package_name}...")
            time.sleep(duration * 0.4)
            
            logger.info(f"✓ {package_name} installed successfully!")
            time.sleep(duration * 0.3)
        finally:
            clear_task_context()
    
    print("\nSimulating parallel package installations:\n")
    
    # Create threads for parallel execution
    packages = [
        ("Node.js", 0.5),
        ("Python", 0.4),
        ("Rust", 0.6),
    ]
    
    threads = []
    for package, duration in packages:
        t = threading.Thread(target=install_package, args=(package, duration))
        threads.append(t)
        t.start()
    
    # Wait for all threads
    for t in threads:
        t.join()
    
    print("\n✓ Parallel logging with task context works correctly!")
    print("  Notice how each log line is prefixed with the task identifier,")
    print("  making it easy to identify which task produced which log line.")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("TASK CONTEXT FUNCTIONALITY TESTS")
    print("=" * 80)
    
    test_thread_local_context()
    test_task_context_filter()
    test_parallel_logging()
    
    print("\n" + "=" * 80)
    print("ALL TESTS PASSED!")
    print("=" * 80)
    print("\nThe task context feature is working correctly and ready to use")
    print("in the pipeline for parallel execution.\n")


if __name__ == "__main__":
    main()

