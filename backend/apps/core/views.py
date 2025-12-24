"""
Core API Views - Health Check and System Status
"""

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


@extend_schema(
    summary="Health Check",
    description="Check the health status of the API and its dependencies",
    responses={
        200: {
            "type": "object",
            "properties": {
                "status": {"type": "string", "example": "healthy"},
                "version": {"type": "string", "example": "0.1.0"},
                "services": {
                    "type": "object",
                    "properties": {
                        "database": {"type": "string", "example": "connected"},
                        "cache": {"type": "string", "example": "connected"},
                    },
                },
            },
        }
    },
)
@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint to verify API and service connectivity.
    Returns status of database and cache connections.
    """
    health_status = {
        "status": "healthy",
        "version": "0.1.0",
        "services": {
            "database": "unknown",
            "cache": "unknown",
        },
    }

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["services"]["database"] = "connected"
    except Exception as e:
        health_status["services"]["database"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis cache connection
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            health_status["services"]["cache"] = "connected"
        else:
            health_status["services"]["cache"] = "error: cache read failed"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["cache"] = f"error: {str(e)}"
        health_status["status"] = "degraded"

    response_status = (
        status.HTTP_200_OK
        if health_status["status"] == "healthy"
        else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return Response(health_status, status=response_status)
