from django.urls import path
from . import views

app_name = "myutils"

urlpatterns = [
    path("healthz/", views.health_check, name="health-check"),
    path("debug/", views.debug_view, name="debug"),
    path("task-status/<str:task_id>/", views.task_status, name="task-status"),
    path("trigger-task/", views.trigger_long_task, name="trigger-task"),
]
