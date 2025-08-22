"""
Constants for the tasks app
"""

# Task Status Choices
TASK_STATUS_ACTIVE = "active"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"

# Task Status Choices List
TASK_STATUS_CHOICES = [
    (TASK_STATUS_ACTIVE, "Active"),
    (TASK_STATUS_COMPLETED, "Completed"),
    (TASK_STATUS_FAILED, "Failed"),
]

# Task Status Labels
TASK_STATUS_LABELS = {
    TASK_STATUS_ACTIVE: "Active",
    TASK_STATUS_COMPLETED: "Completed", 
    TASK_STATUS_FAILED: "Failed",
}

# Task Status Colors (for Bootstrap badges)
TASK_STATUS_COLORS = {
    TASK_STATUS_ACTIVE: "success",
    TASK_STATUS_COMPLETED: "info",
    TASK_STATUS_FAILED: "danger",
}

# Validation Messages
VALIDATION_MESSAGES = {
    "future_date_required": "Date must be in the future",
    "task_not_found": "Task not found",
    "task_not_owned": "You don't have permission to access this task",
    "only_active_editable": "Only active tasks can be edited",
    "unable_to_complete": "Unable to complete task",
    "unable_to_reactivate": "Unable to reactivate task",
    "unable_to_delete": "Unable to delete task",
}
