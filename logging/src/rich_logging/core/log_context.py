"""Thread-local context storage for logging.

This module provides thread-safe storage for task/step context that can be
included in log messages. This is particularly useful for parallel execution
where multiple tasks run concurrently and need to be identified in the logs.
"""

import threading
from typing import Any


class LogContext:
    """Thread-local storage for logging context.
    
    This class uses threading.local() to store context data per thread,
    ensuring that parallel tasks can have independent context without
    interfering with each other.
    """
    
    _thread_local = threading.local()
    
    @classmethod
    def set_task_context(
        cls,
        step_id: str,
        task_name: str | None = None,
        **extra_context: Any
    ) -> None:
        """Set the task context for the current thread.
        
        Args:
            step_id: The unique identifier for the current step/task
            task_name: Optional human-readable task name
            **extra_context: Additional context data to store
        """
        context = {
            "step_id": step_id,
            "task_name": task_name or step_id,
            **extra_context
        }
        cls._thread_local.context = context
    
    @classmethod
    def get_task_context(cls) -> dict[str, Any] | None:
        """Get the task context for the current thread.
        
        Returns:
            Dictionary containing the task context, or None if no context is set
        """
        return getattr(cls._thread_local, "context", None)
    
    @classmethod
    def clear_task_context(cls) -> None:
        """Clear the task context for the current thread."""
        if hasattr(cls._thread_local, "context"):
            delattr(cls._thread_local, "context")
    
    @classmethod
    def get_step_id(cls) -> str | None:
        """Get the current step ID.
        
        Returns:
            The step ID if context is set, None otherwise
        """
        context = cls.get_task_context()
        return context.get("step_id") if context else None
    
    @classmethod
    def get_task_name(cls) -> str | None:
        """Get the current task name.
        
        Returns:
            The task name if context is set, None otherwise
        """
        context = cls.get_task_context()
        return context.get("task_name") if context else None


# Convenience functions for easier imports
def set_task_context(
    step_id: str,
    task_name: str | None = None,
    **extra_context: Any
) -> None:
    """Set the task context for the current thread.
    
    Args:
        step_id: The unique identifier for the current step/task
        task_name: Optional human-readable task name
        **extra_context: Additional context data to store
    """
    LogContext.set_task_context(step_id, task_name, **extra_context)


def get_task_context() -> dict[str, Any] | None:
    """Get the task context for the current thread.
    
    Returns:
        Dictionary containing the task context, or None if no context is set
    """
    return LogContext.get_task_context()


def clear_task_context() -> None:
    """Clear the task context for the current thread."""
    LogContext.clear_task_context()


def get_step_id() -> str | None:
    """Get the current step ID.
    
    Returns:
        The step ID if context is set, None otherwise
    """
    return LogContext.get_step_id()


def get_task_name() -> str | None:
    """Get the current task name.
    
    Returns:
        The task name if context is set, None otherwise
    """
    return LogContext.get_task_name()

