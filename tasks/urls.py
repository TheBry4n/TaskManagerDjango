from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path("", views.task_list, name="task_list"),
    path("create/", views.task_create, name="task_create"),
    # Place specific routes before parameterized ones to avoid shadowing
    path("api/status/", views.api_task_status, name="api_task_status"),
    path("<str:task_id>/", views.task_detail, name="task_detail"),
    path("<str:task_id>/update/", views.task_update, name="task_update"),
    path("<str:task_id>/complete/", views.task_complete, name="task_complete"),
    path("<str:task_id>/reactivate/", views.reactivate_task, name="reactivate_task"),
    path("<str:task_id>/delete/", views.task_delete, name="task_delete"),
]