from django.utils import timezone
from django.db.models import QuerySet
from django.contrib.auth.models import User
from typing import Optional
from .models import Task
from .core.base_repository import BaseRepository
from .constants import TASK_STATUS_ACTIVE, TASK_STATUS_COMPLETED, TASK_STATUS_FAILED

class TaskRepository(BaseRepository[Task]):
    """Repository for Task model"""

    def __init__(self):
        super().__init__(Task)
    
    def get_tasks_by_status_and_user(self, status: str, user: User) -> QuerySet[Task]:
        """Get tasks by status for a specific user"""
        return self.filter(status=status, user=user)
    
    def get_active_tasks_by_user(self, user: User) -> QuerySet[Task]:
        """Get all active tasks for a user"""
        return self.get_tasks_by_status_and_user(TASK_STATUS_ACTIVE, user)
    
    def get_completed_tasks_by_user(self, user: User) -> QuerySet[Task]:
        """Get all completed tasks for a user"""
        return self.get_tasks_by_status_and_user(TASK_STATUS_COMPLETED, user)
    
    def get_failed_tasks_by_user(self, user: User) -> QuerySet[Task]:
        """Get all failed tasks for a user"""
        return self.get_tasks_by_status_and_user(TASK_STATUS_FAILED, user)
    
    def get_overdue_tasks_by_user(self, user: User) -> QuerySet[Task]:
        """Get all overdue tasks (regardless of status) using local time"""
        now = timezone.localtime(timezone.now())
        return self.filter(user=user, due_date__lt=now)
    
    def get_tasks_by_status(self, status: str) -> QuerySet[Task]:
        """Get tasks by status (all users)"""
        return self.filter(status=status)
    
    def get_active_tasks(self) -> QuerySet[Task]:
        """Get only active tasks (all users)"""
        return self.get_tasks_by_status(TASK_STATUS_ACTIVE)
    
    def get_completed_tasks(self) -> QuerySet[Task]:
        """Get only completed tasks (all users)"""
        return self.get_tasks_by_status(TASK_STATUS_COMPLETED)
    
    def get_failed_tasks(self) -> QuerySet[Task]:
        """Get only failed tasks (all users)"""
        return self.get_tasks_by_status(TASK_STATUS_FAILED)
    
    def get_overdue_tasks(self) -> QuerySet[Task]:
        """Get overdue tasks (all users) using local time"""
        now = timezone.localtime(timezone.now())
        return self.filter(due_date__lt=now)
    
    def update_task_status(self) -> int:
        """
        Automatically update task status based on due date and current date.
        Returns the number of tasks that were updated.
        """
        # Find all active tasks that are overdue using local time
        now = timezone.localtime(timezone.now())
        overdue_active_tasks = self.filter(
            status=TASK_STATUS_ACTIVE, 
            due_date__lt=now
        )
        
        updated_count = overdue_active_tasks.count()
        
        if updated_count > 0:
            # Update all overdue active tasks to failed status
            overdue_active_tasks.update(status="failed")
        
        return updated_count
    
    def ensure_overdue_tasks_are_failed(self) -> int:
        """
        Ensure all overdue tasks are marked as failed.
        This is a more comprehensive method that checks all tasks.
        Returns the number of tasks that were updated.
        """
        # Find all overdue tasks that are still active using local time
        now = timezone.localtime(timezone.now())
        overdue_active_tasks = self.filter(
            status="active", 
            due_date__lt=now
        )
        
        updated_count = overdue_active_tasks.count()
        
        if updated_count > 0:
            # Use bulk update for better performance
            tasks_to_update = list(overdue_active_tasks)
            for task in tasks_to_update:
                task.status = TASK_STATUS_FAILED
            
            self.bulk_update(tasks_to_update, ['status'])
        
        return updated_count
    
    def force_update_all_overdue_tasks(self) -> int:
        """Force update all overdue tasks regardless of current status"""
        all_overdue_tasks = self.filter(due_date__lt=timezone.now())
        active_overdue_tasks = all_overdue_tasks.filter(status=TASK_STATUS_ACTIVE)
        updated_count = active_overdue_tasks.count()
        if updated_count > 0:
            active_overdue_tasks.update(status=TASK_STATUS_FAILED)
        return updated_count
    
    def complete_task(self, task_id: str, user: User) -> Optional[Task]:
        """Mark a task as completed"""
        task = self.get_by_id(task_id)
        if task and task.user == user and task.status != TASK_STATUS_COMPLETED:
            return self.update(task, status=TASK_STATUS_COMPLETED)
        return None
    
    def reactivate_task(self, task_id: str, user: User, new_due_date) -> Optional[Task]:
        """Reactivate a failed task with a new date"""
        task = self.get_by_id(task_id)
        if task and task.user == user and task.status == TASK_STATUS_FAILED and new_due_date > timezone.now():
            task.reactivation_count += 1
            return self.update(
                task, 
                status=TASK_STATUS_ACTIVE, 
                due_date=new_due_date, 
                reactivation_count=task.reactivation_count
            )
        return None
