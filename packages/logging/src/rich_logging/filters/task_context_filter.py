"""Logging filter to add task context to log messages.

This filter prepends task identifiers to log messages when executing
parallel tasks, making it easy to identify which task produced which log line.
"""

import logging
from typing import Any

from ..core.log_context import LogContext


class TaskContextFilter(logging.Filter):
    """Filter that adds task context to log messages.
    
    This filter checks for thread-local task context and prepends
    the task identifier to log messages. This is particularly useful
    for parallel execution where multiple tasks run concurrently.
    
    Example:
        Without filter: "Installing package..."
        With filter: "[install_nodejs] Installing package..."
    """
    
    def __init__(
        self,
        name: str = "",
        enabled: bool = True,
        format_template: str = "[{task_name}] ",
        use_rich_markup: bool = True,
        task_style: str = "cyan",
    ):
        """Initialize the task context filter.
        
        Args:
            name: Filter name (passed to parent Filter class)
            enabled: Whether the filter is enabled
            format_template: Template for formatting the task context.
                           Available placeholders: {step_id}, {task_name}
            use_rich_markup: Whether to use Rich markup for styling
            task_style: Rich style to apply to task identifier (e.g., "cyan", "bold blue")
        """
        super().__init__(name)
        self.enabled = enabled
        self.format_template = format_template
        self.use_rich_markup = use_rich_markup
        self.task_style = task_style
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Filter the log record, adding task context if available.
        
        Args:
            record: The log record to filter
            
        Returns:
            True to allow the record to be logged
        """
        if not self.enabled:
            return True
        
        # Get task context from thread-local storage
        context = LogContext.get_task_context()
        
        if context:
            # Format the task identifier
            task_identifier = self.format_template.format(**context)
            
            # Apply Rich markup if enabled
            if self.use_rich_markup and self.task_style:
                task_identifier = f"[{self.task_style}]{task_identifier}[/{self.task_style}]"
            
            # Prepend to the message
            record.msg = f"{task_identifier}{record.msg}"
            
            # Also add to record for potential use by formatters
            if not hasattr(record, "task_context"):
                record.task_context = context  # type: ignore[attr-defined]
        
        return True
    
    def enable(self) -> None:
        """Enable the filter."""
        self.enabled = True
    
    def disable(self) -> None:
        """Disable the filter."""
        self.enabled = False
    
    def set_format_template(self, template: str) -> None:
        """Set the format template.
        
        Args:
            template: New format template with placeholders like {step_id}, {task_name}
        """
        self.format_template = template
    
    def set_style(self, style: str) -> None:
        """Set the Rich style for task identifiers.
        
        Args:
            style: Rich style string (e.g., "cyan", "bold blue", "dim")
        """
        self.task_style = style

