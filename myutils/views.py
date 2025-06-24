from django.db import transaction
from django.views.decorators.cache import never_cache

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@transaction.non_atomic_requests
@api_view(["GET"])
@never_cache
@permission_classes([AllowAny])
def health_check(request):
    return Response(status=status.HTTP_200_OK)
