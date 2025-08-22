from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task
from .repository import TaskRepository
from .forms import TaskForm, TaskReactivationForm
from .utils import get_task_statistics, format_task_message
from .constants import TASK_STATUS_ACTIVE, TASK_STATUS_FAILED, VALIDATION_MESSAGES

@login_required
def task_list(request):
    """View for listing all tasks"""
    repository = TaskRepository()
    
    # Ensure all overdue tasks are properly marked as failed
    updated_count = repository.ensure_overdue_tasks_are_failed()
    
    if updated_count > 0:
        messages.info(request, f'{updated_count} overdue task(s) have been marked as failed.')

    # Get task statistics using utility function
    context = get_task_statistics(request.user)

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
            
            # Check if the newly created task is overdue and update it immediately
            if task.is_overdue:
                task.status = TASK_STATUS_FAILED
                task.save()
                messages.success(request, format_task_message("created", task.title, "Marked as failed - overdue"))
            else:
                messages.success(request, format_task_message("created", task.title))
            
            return redirect("tasks:task_list")
    else:
        form = TaskForm()
    
    return render(request, "tasks/task_form.html", {"form" : form, "action" : "Create"})

@login_required
def task_detail(request, task_id):
    """Display task details"""
    repository = TaskRepository()
    
    # Ensure all overdue tasks are properly marked as failed
    repository.ensure_overdue_tasks_are_failed()
    
    task = repository.get_by_id(task_id)

    if not task or task.user != request.user:
        messages.error(request, 'Task not found.')
        return redirect("tasks:task_list")
    
    reactivation_form = TaskReactivationForm() if task.status == TASK_STATUS_FAILED else None

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
        messages.success(request, format_task_message("marked as completed", task.title))
    else:
        messages.error(request, VALIDATION_MESSAGES['unable_to_complete'])
    
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
            messages.success(request, format_task_message("reactivated", task.title))
        else:
            messages.error(request, VALIDATION_MESSAGES['unable_to_reactivate'])
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
    if task.status != TASK_STATUS_ACTIVE:
        messages.error(request, VALIDATION_MESSAGES['only_active_editable'])
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
            messages.success(request, format_task_message("updated", updated_task.title))
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
        messages.success(request, format_task_message("deleted", task_title))
    else:
        messages.error(request, VALIDATION_MESSAGES['unable_to_delete'])
    
    return redirect("tasks:task_list")

@login_required
def api_task_status(request):
    """API endpoint for task status"""
    repository = TaskRepository()

    # Ensure all overdue tasks are properly marked as failed
    updated_count = repository.ensure_overdue_tasks_are_failed()
    
    # Get clean counts after status update
    active_count = repository.get_active_tasks_by_user(request.user).count()
    completed_count = repository.get_completed_tasks_by_user(request.user).count()
    failed_count = repository.get_failed_tasks_by_user(request.user).count()

    return JsonResponse({
        'updated_count': updated_count,
        'active_count': active_count,
        'completed_count': completed_count,
        'failed_count': failed_count,
    })


