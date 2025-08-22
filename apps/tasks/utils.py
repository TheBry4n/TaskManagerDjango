from django.utils import timezone
from django import forms
from typing import Any


def validate_future_datetime(datetime_value: Any, field_name: str = "datetime") -> Any:
    """
    Common validation for future datetime fields
    
    Args:
        datetime_value: The datetime value to validate
        field_name: Name of the field for error message
        
    Returns:
        The validated datetime value
        
    Raises:
        forms.ValidationError: If datetime is not in the future
    """
    if datetime_value and datetime_value <= timezone.now():
        raise forms.ValidationError(
            f"{field_name.replace('_', ' ').title()} must be in the future"
        )
    return datetime_value


def get_task_statistics(user) -> dict:
    """
    Get task statistics for a user
    
    Args:
        user: User instance
        
    Returns:
        dict: Dictionary with task counts
    """
    from .repository import TaskRepository
    repository = TaskRepository()
    
    active_tasks = repository.get_active_tasks_by_user(user)
    completed_tasks = repository.get_completed_tasks_by_user(user)
    failed_tasks = repository.get_failed_tasks_by_user(user)
    
    return {
        "active_tasks": active_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "total_tasks": active_tasks.count() + completed_tasks.count() + failed_tasks.count(),
    }


def format_task_message(action: str, task_title: str, additional_info: str = "") -> str:
    """
    Format consistent task messages
    
    Args:
        action: The action performed (created, updated, deleted, etc.)
        task_title: The title of the task
        additional_info: Additional information to append
        
    Returns:
        str: Formatted message
    """
    message = f'Task "{task_title}" {action} successfully!'
    if additional_info:
        message += f" ({additional_info})"
    return message
