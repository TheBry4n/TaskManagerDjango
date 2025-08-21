from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task
from .repository import TaskRepository
from .forms import TaskForm, TaskReactivationForm
from django.utils import timezone

@login_required
def task_list(request):
    """View for listing all tasks"""
    repository = TaskRepository()
    
    # Update task status automatically (check for overdue tasks)
    repository.update_task_status()

    # Get tasks by status
    active_tasks_qs = repository.get_active_tasks_by_user(request.user)
    completed_tasks = repository.get_completed_tasks_by_user(request.user)
    failed_tasks = repository.get_failed_tasks_by_user(request.user)

    # Split active tasks into on-time and overdue for display purposes
    now = timezone.now()
    active_tasks = active_tasks_qs.filter(due_date__gte=now)
    overdue_active_tasks = active_tasks_qs.filter(due_date__lt=now)

    failed_count = failed_tasks.count() + overdue_active_tasks.count()

    context = {
        "active_tasks" : active_tasks,
        "completed_tasks" : completed_tasks,
        "failed_tasks" : failed_tasks,
        "overdue_active_tasks": overdue_active_tasks,
        "failed_count": failed_count,
        "total_tasks" : active_tasks.count() + completed_tasks.count() + failed_count,
    }

    return render(request, "tasks/task_list.html", context)

@login_required
def task_create(request):
    """View for creating a new task"""
    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            repository = TaskRepository()
            task = repository.create(
                user = request.user,
                title = form.cleaned_data["title"],
                description = form.cleaned_data["description"],
                due_date = form.cleaned_data["due_date"],
            )
            messages.success(request, f'Task "{task.title}" created successfully!')
            return redirect("tasks:task_list")
    else:
        form = TaskForm()
    
    return render(request, "tasks/task_form.html", {"form" : form, "action" : "Create"})

@login_required
def task_detail(request, task_id):
    """Display task details"""
    repository = TaskRepository()
    
    # Update task status automatically (check for overdue tasks)
    repository.update_task_status()
    
    task = repository.get_by_id(task_id)

    if not task or task.user != request.user:
        messages.error(request, 'Task not found.')
        return redirect("tasks:task_list")
    
    reactivation_form = TaskReactivationForm() if task.status == "failed" else None

    context = {
        "task" : task,
        "reactivation_form" : reactivation_form,
    }

    return render(request, "tasks/task_detail.html", context)

@login_required
@require_POST
def task_complete(request, task_id):
    """Mark a task as completed"""
    repository = TaskRepository()
    task = repository.complete_task(task_id, request.user)
    
    if task:
        messages.success(request, f'Task "{task.title}" marked as completed!')
    else:
        messages.error(request, 'Unable to complete task.')
    
    return redirect("tasks:task_list")

@login_required
@require_POST
def reactivate_task(request, task_id):
    """Reactivate a failed task"""
    repository = TaskRepository()
    form = TaskReactivationForm(request.POST)

    if form.is_valid():
        task = repository.reactivate_task(
            task_id, 
            request.user, 
            form.cleaned_data["new_due_date"]
        )

        if task:
            messages.success(request, f'Task "{task.title}" reactivated successfully!')
        else:
            messages.error(request, 'Unable to reactivate task.')
    else:
        messages.error(request, 'Invalid due date.')
    
    return redirect('tasks:task_detail', task_id=task_id)

@login_required
def task_update(request, task_id):
    """Update an existing task (only active tasks)"""
    repository = TaskRepository()
    task = repository.get_by_id(task_id)
    
    if not task or task.user != request.user:
        messages.error(request, 'Task not found.')
        return redirect("tasks:task_list")
    
    # Only allow editing active tasks
    if task.status != 'active':
        messages.error(request, 'Only active tasks can be edited.')
        return redirect("tasks:task_detail", task_id=task_id)
    
    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            updated_task = repository.update(
                task,
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                due_date=form.cleaned_data["due_date"]
            )
            messages.success(request, f'Task "{updated_task.title}" updated successfully!')
            return redirect("tasks:task_detail", task_id=task_id)
    else:
        form = TaskForm(instance=task)
    
    return render(request, "tasks/task_form.html", {"form": form, "action": "Update", "task": task})

@login_required
def task_delete(request, task_id):
    """Delete a task (any status)"""
    repository = TaskRepository()
    task = repository.get_by_id(task_id)
    
    if task and task.user == request.user:
        task_title = task.title
        repository.delete(task)
        messages.success(request, f'Task "{task_title}" deleted successfully!')
    else:
        messages.error(request, "Unable to delete task.")
    
    return redirect("tasks:task_list")

@login_required
def api_task_status(request):
    """API endpoint for task status"""
    repository = TaskRepository()

    updated_count = repository.update_task_status()
    # Counts aligned with display logic
    active_qs = repository.get_active_tasks_by_user(request.user)
    now = timezone.now()
    active_count = active_qs.filter(due_date__gte=now).count()
    completed_count = repository.get_completed_tasks_by_user(request.user).count()
    failed_count = (
        repository.get_failed_tasks_by_user(request.user).count() +
        active_qs.filter(due_date__lt=now).count()
    )

    return JsonResponse({
        'updated_count': updated_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'failed_count': failed_count,
    })
