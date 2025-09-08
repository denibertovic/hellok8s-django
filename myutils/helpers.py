import os
from django.conf import settings


def get_upload_rate_limit(group, request):
    """Return rate limit based on user plan."""
    if request.user.is_authenticated:
        plan = request.user.plan
        return settings.PLAN_OPTIONS.get(plan, {}).get("upload_rate_limit", "50/m")
    else:
        return settings.ANONYMOUS_UPLOAD_RATE_LIMIT


def get_finalize_rate_limit(group, request):
    """Return higher rate limit for finalization (batch uploads need this)."""
    if request.user.is_authenticated:
        plan = request.user.plan
        return settings.PLAN_OPTIONS.get(plan, {}).get("finalize_rate_limit", "500/m")
    else:
        return settings.ANONYMOUS_UPLOAD_RATE_LIMIT


def has_spam_trigger_in_text(text):
    triggers = ["http://", "https://", "www"]
    if any([trigger in text for trigger in triggers]):
        return True
    return False


def has_tld_domain_in_text(text):
    with open(
        os.path.join(os.path.dirname(__file__), "iana_list_of_toplevel_domains.txt")
    ) as f:
        content = f.read()
        domains = content.splitlines()
        if any([tld in text for tld in domains]):
            return True
    return False
