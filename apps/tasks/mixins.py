from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.models import User
from typing import Optional
from .models import Task


class TaskAccessMixin:
    """Mixin for common task access and validation logic"""
    
    def get_task_or_redirect(self, task_id: str, user: User, error_message: str = 'Task not found.') -> Optional[Task]:
        """Get task by ID and user, redirect if not found or not owned by user"""
        from .repository import TaskRepository
        repository = TaskRepository()
        task = repository.get_by_id(task_id)
        
        if not task or task.user != user:
            messages.error(self.request, error_message)
            return None
            
        return task
    
    def ensure_user_owns_task(self, task: Task, user: User) -> bool:
        """Check if user owns the task"""
        return task.user == user


class OverdueTaskMixin:
    """Mixin for handling overdue task updates"""
    
    def update_overdue_tasks(self):
        """Update overdue tasks and return count of updated tasks"""
        from .repository import TaskRepository
        repository = TaskRepository()
        updated_count = repository.ensure_overdue_tasks_are_failed()
        
        if updated_count > 0:
            messages.info(self.request, f'{updated_count} overdue task(s) have been marked as failed.')
        
        return updated_count


class TaskStatusMixin:
    """Mixin for task status validation"""
    
    def validate_task_status(self, task: Task, allowed_statuses: list, error_message: str) -> bool:
        """Validate if task has allowed status"""
        if task.status not in allowed_statuses:
            messages.error(self.request, error_message)
            return False
        return True
