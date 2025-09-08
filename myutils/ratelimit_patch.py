"""
Local monkey-patch for django-ratelimit to add retry timing information to requests.
This enhances the existing decorator without forking the library.
"""

from functools import wraps

from django.conf import settings
from django.utils.module_loading import import_string

from django_ratelimit import ALL, UNSAFE
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import is_ratelimited, get_usage


def enhanced_ratelimit(group=None, key=None, rate=None, method=ALL, block=True):
    """
    Enhanced ratelimit decorator that adds retry timing info to the request.
    Drop-in replacement for django_ratelimit.decorators.ratelimit
    Becuase this issue is not addressed yet: https://github.com/jsocol/django-ratelimit/issues/165
    """

    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, "limited", False)
            ratelimited = is_ratelimited(
                request=request,
                group=group,
                fn=fn,
                key=key,
                rate=rate,
                method=method,
                increment=True,
            )
            request.limited = ratelimited or old_limited

            if ratelimited and block:
                # NEW: Get timing info and store on request
                usage = get_usage(
                    request=request,
                    group=group,
                    fn=fn,
                    key=key,
                    rate=rate,
                    method=method,
                    increment=False,
                )
                if usage and "time_left" in usage:
                    request.ratelimit_retry_after = max(1, int(usage["time_left"]))
                else:
                    request.ratelimit_retry_after = 60  # fallback

                cls = getattr(settings, "RATELIMIT_EXCEPTION_CLASS", Ratelimited)
                raise (import_string(cls) if isinstance(cls, str) else cls)()
            return fn(request, *args, **kw)

        return _wrapped

    return decorator


# Add the same attributes as the original decorator
enhanced_ratelimit.ALL = ALL
enhanced_ratelimit.UNSAFE = UNSAFE
