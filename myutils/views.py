import socket
import time
import inspect
import re
from django.db import transaction
from django.shortcuts import render
from django.views.decorators.cache import never_cache
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.urls import resolve
from django_ratelimit.decorators import ratelimit
from celery.result import AsyncResult

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .tasks import simulate_long_task


def parse_rate(rate_string):
    """Parse rate string like '1/m', '5/h', '10/s' to get period in seconds."""
    if "/" not in rate_string:
        return 1  # Default to 1 second if no format specified

    _, period_str = rate_string.split("/", 1)

    # Extract number and unit from period string
    import re

    match = re.match(r"(\d*)([smhd]?)", period_str)
    if not match:
        return 1

    number_str, unit = match.groups()
    number = int(number_str) if number_str else 1

    # Convert to seconds
    unit_multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400,
        "": 1,  # Default to seconds if no unit
    }

    return number * unit_multipliers.get(unit, 1)


def get_view_ratelimit_from_source(view_func):
    """Extract rate limit from view function by inspecting its source code."""
    try:
        source = inspect.getsource(view_func)
        # Look for @ratelimit decorator pattern
        ratelimit_match = re.search(
            r'@ratelimit\([^)]*rate=["\']([^"\'][^"\']*)["\'\]][^)]*\)', source
        )
        if ratelimit_match:
            return ratelimit_match.group(1)
    except (OSError, TypeError):
        # Source not available or function not found
        pass
    return None


def get_dynamic_rate_limit(request):
    """Dynamically determine the rate limit for the current view."""
    try:
        # Get the view function from the request
        if hasattr(request, "resolver_match") and request.resolver_match:
            view_func = request.resolver_match.func

            # Try to get the rate from the source code
            rate = get_view_ratelimit_from_source(view_func)
            if rate:
                return rate

        # Fallback: try resolving the URL again
        resolved = resolve(request.path_info)
        if resolved and resolved.func:
            rate = get_view_ratelimit_from_source(resolved.func)
            if rate:
                return rate

    except Exception:
        pass

    return None


def ratelimit_view(request, exception):
    """Custom ratelimit view that returns 429 with Retry-After header. This whole thing
    is a stupid hack since django-ratelimit doesn't inject this via it's middleware as it should."""
    # Default retry time
    retry_after_seconds = 60

    # Try to dynamically determine the rate limit
    rate_string = get_dynamic_rate_limit(request)
    if rate_string:
        retry_after_seconds = parse_rate(rate_string)
    else:
        # Fallback to static mapping for views we can't inspect dynamically
        view_path = (
            request.resolver_match.view_name if request.resolver_match else "unknown"
        )
        view_rates = {
            "trigger_long_task": "1/2m",  # 1 per 2 minutes
            # Add other rate-limited views here as needed
        }

        # Try to determine the rate from the view
        for view_name, fallback_rate_string in view_rates.items():
            if view_name in str(request.path) or view_name in view_path:
                retry_after_seconds = parse_rate(fallback_rate_string)
                break

    # Get the client IP to create a cache key similar to django-ratelimit
    client_ip = request.META.get("REMOTE_ADDR")
    # Create cache key that matches django-ratelimit's format
    cache_key = f"rl:ip:{client_ip}:{request.path}"

    # Try to get more precise timing from cache
    rate_limit_data = cache.get(cache_key)
    if rate_limit_data:
        # If we have cache data, calculate remaining time more precisely
        if isinstance(rate_limit_data, (int, float)):
            # Simple counter case - estimate based on when it will reset
            current_time = int(time.time())
            # Estimate reset time (this is approximate)
            reset_time = (current_time // retry_after_seconds + 1) * retry_after_seconds
            retry_after_seconds = max(1, reset_time - current_time)

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
