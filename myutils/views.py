import socket
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from celery.result import AsyncResult

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .tasks import simulate_long_task


@transaction.non_atomic_requests
@api_view(["GET"])
@never_cache
@permission_classes([AllowAny])
def health_check(request):
    return Response(status=status.HTTP_200_OK)


def debug_view(request):
    """Debug view showing server hostname for Kubernetes load balancing demo."""
    hostname = socket.gethostname()

    context = {
        "hostname": hostname,
    }

    return render(request, "myutils/debug.html", context)


def task_status(request, task_id):
    """Check the status of a Celery task."""
    result = AsyncResult(task_id)

    response_data = {
        "task_id": task_id,
        "status": result.status,
        "result": result.result if result.ready() else None,
    }

    return JsonResponse(response_data)


@ratelimit(key="ip", rate="1/m", method=["GET", "POST"])
def trigger_long_task(request):
    """Trigger a long-running Celery task. Rate limited to 1 request per minute (disabled in DEBUG mode via RATELIMIT_ENABLE)."""
    task_result = simulate_long_task.delay()

    return JsonResponse(
        {
            "task_id": task_result.id,
            "status": "Task started",
            "message": "Long task has been queued for processing",
        }
    )
