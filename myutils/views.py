import socket
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from .ratelimit_patch import enhanced_ratelimit as ratelimit
from celery.result import AsyncResult

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .tasks import simulate_long_task


def ratelimit_view(request, exception):
    """Custom ratelimit view that returns 429 with Retry-After header."""
    # Get retry timing from our enhanced decorator, with fallback
    retry_after_seconds = getattr(request, "ratelimit_retry_after", 60)

    response = HttpResponse(
        "Rate limit exceeded. Please try again later.",
        status=429,
        content_type="text/plain",
    )
    response["Retry-After"] = str(retry_after_seconds)

    return response


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


@ratelimit(key="ip", rate="1/2m", method=["GET", "POST"])
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
