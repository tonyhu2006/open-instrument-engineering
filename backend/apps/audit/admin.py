from django.contrib import admin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Read-only: audit records are append-only (ADM-07)."""

    list_display = ["timestamp", "user", "action", "model_name", "object_id"]
    list_filter = ["action", "model_name", "organization"]
    search_fields = ["object_repr", "user__username"]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
