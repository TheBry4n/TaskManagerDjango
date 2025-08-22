from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Task(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="Title")
    description = models.TextField(blank=True, verbose_name="Description")
    due_date = models.DateTimeField(verbose_name="Due Date")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active", verbose_name="Status")
    reactivation_count = models.PositiveIntegerField(default=0, verbose_name="Reactivation Count")
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tasks',
        verbose_name="User"
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    @property
    def is_overdue(self):
        """Check if the task is overdue using local time"""
        now = timezone.localtime(timezone.now())
        due_local = timezone.localtime(self.due_date)
        return now > due_local
    
    @property
    def days_until_due(self):
        """Calculate the number of days until the task is due using local time"""
        now = timezone.localtime(timezone.now())
        due_local = timezone.localtime(self.due_date)
        delta = due_local - now
        return delta.days
    
    @property
    def overdue_days(self):
        """Calculate the number of days the task is overdue (positive number) using local time"""
        if self.is_overdue:
            return abs(self.days_until_due)
        return 0
