from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Task
from .repository import TaskRepository

# Create your tests here.

class TaskRepositoryTest(TestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.repository = TaskRepository()
        
        # Create test tasks
        self.active_task = self.repository.create(
            user=self.user,
            title="Active Task",
            description="This is an active task",
            due_date=timezone.now() + timedelta(days=1)
        )
        
        self.overdue_task = self.repository.create(
            user=self.user,
            title="Overdue Task",
            description="This is an overdue task",
            due_date=timezone.now() - timedelta(days=1)
        )
        
        self.completed_task = self.repository.create(
            user=self.user,
            title="Completed Task",
            description="This is a completed task",
            due_date=timezone.now() + timedelta(days=1)
        )
        self.repository.update(self.completed_task, status="completed")

    def test_ensure_overdue_tasks_are_failed(self):
        """Test that overdue tasks are properly marked as failed"""
        # Initially, overdue task should still be active
        self.assertEqual(self.overdue_task.status, "active")
        
        # Run the method to update overdue tasks
        updated_count = self.repository.ensure_overdue_tasks_are_failed()
        
        # Should have updated 1 task
        self.assertEqual(updated_count, 1)
        
        # Refresh the overdue task from database
        self.overdue_task.refresh_from_db()
        
        # The overdue task should now be failed
        self.assertEqual(self.overdue_task.status, "failed")
        
        # The active task should still be active
        self.active_task.refresh_from_db()
        self.assertEqual(self.active_task.status, "active")
        
        # The completed task should still be completed
        self.completed_task.refresh_from_db()
        self.assertEqual(self.completed_task.status, "completed")

    def test_get_active_tasks_by_user(self):
        """Test getting active tasks for a user"""
        active_tasks = self.repository.get_active_tasks_by_user(self.user)
        self.assertEqual(active_tasks.count(), 2)  # active_task and overdue_task (before update)
        
        # After updating overdue tasks
        self.repository.ensure_overdue_tasks_are_failed()
        active_tasks = self.repository.get_active_tasks_by_user(self.user)
        self.assertEqual(active_tasks.count(), 1)  # only active_task

    def test_get_failed_tasks_by_user(self):
        """Test getting failed tasks for a user"""
        failed_tasks = self.repository.get_failed_tasks_by_user(self.user)
        self.assertEqual(failed_tasks.count(), 0)  # no failed tasks initially
        
        # After updating overdue tasks
        self.repository.ensure_overdue_tasks_are_failed()
        failed_tasks = self.repository.get_failed_tasks_by_user(self.user)
        self.assertEqual(failed_tasks.count(), 1)  # overdue_task should now be failed

    def test_task_properties(self):
        """Test task model properties"""
        # Test overdue task properties
        self.assertTrue(self.overdue_task.is_overdue)
        self.assertGreater(self.overdue_task.overdue_days, 0)
        
        # Test active task properties
        self.assertFalse(self.active_task.is_overdue)
        self.assertEqual(self.active_task.overdue_days, 0)
        self.assertGreaterEqual(self.active_task.days_until_due, 0)

    def test_reactivate_task(self):
        """Test reactivating a failed task"""
        # First, make the overdue task failed
        self.repository.ensure_overdue_tasks_are_failed()
        self.overdue_task.refresh_from_db()
        self.assertEqual(self.overdue_task.status, "failed")
        
        # Reactivate with a new due date
        new_due_date = timezone.now() + timedelta(days=2)
        reactivated_task = self.repository.reactivate_task(
            str(self.overdue_task.id),
            self.user,
            new_due_date
        )
        
        self.assertIsNotNone(reactivated_task)
        self.assertEqual(reactivated_task.status, "active")
        self.assertEqual(reactivated_task.reactivation_count, 1)
        self.assertEqual(reactivated_task.due_date, new_due_date)

    def test_complete_task(self):
        """Test completing a task"""
        completed_task = self.repository.complete_task(
            str(self.active_task.id),
            self.user
        )
        
        self.assertIsNotNone(completed_task)
        self.assertEqual(completed_task.status, "completed")
        
        # Verify it's now in completed tasks
        completed_tasks = self.repository.get_completed_tasks_by_user(self.user)
        self.assertEqual(completed_tasks.count(), 2)  # original + newly completed
