"""
Audit writer — SPECIFICATION §4.1.13 / §6.1.2.

Every create / update / delete performed through the service layer calls
``record()`` inside the same transaction as the data change, so an audit row
exists if and only if the change was committed.
"""

from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Any

from django.core.serializers.json import DjangoJSONEncoder
from django.db import connection
from django.db.models.fields.files import FieldFile
from django_tenants.utils import get_public_schema_name

from .models import AuditLog

_SKIP_FIELDS = {"created_at", "updated_at", "row_version", "lft", "rght", "tree_id"}


def _json_safe(value: Any) -> Any:
    return json.loads(json.dumps(value, cls=DjangoJSONEncoder))


def snapshot(instance) -> dict:
    """Concrete-field snapshot of a model instance (JSON-safe)."""
    data = {}
    for field in instance._meta.concrete_fields:
        if field.name in _SKIP_FIELDS or field.name == "password":
            continue
        value = getattr(instance, field.attname)
        if isinstance(value, FieldFile):
            value = value.name or None
        data[field.attname] = value
    return _json_safe(data)


def _labels(model) -> dict:
    labels = {}
    for field in model._meta.concrete_fields:
        labels[field.attname] = str(getattr(field, "verbose_name", field.name))
    return labels


def _is_number(value) -> bool:
    return isinstance(value, (int, float, Decimal)) and not isinstance(value, bool)


def build_change_details(old: dict, new: dict, labels: dict | None = None) -> dict:
    """Build the §6.1.2 ``change_details`` structure."""
    labels = labels or {}
    changes = []
    added = removed = modified = 0
    for field in sorted(set(old) | set(new)):
        before, after = old.get(field), new.get(field)
        if before == after:
            continue
        empty_before = before in (None, "", [], {})
        empty_after = after in (None, "", [], {})
        if empty_before and not empty_after:
            change_type = "added"
            added += 1
        elif empty_after and not empty_before:
            change_type = "removed"
            removed += 1
        else:
            change_type = "modified"
            modified += 1
        entry = {
            "field": field,
            "field_label": labels.get(field, field),
            "old_value": before,
            "new_value": after,
            "change_type": change_type,
        }
        if change_type == "modified" and _is_number(before) and _is_number(after):
            if before:
                entry["change_percent"] = round(
                    (float(after) - float(before)) / abs(float(before)) * 100, 4
                )
        changes.append(entry)
    return {
        "changed_fields": [c["field"] for c in changes],
        "changes": changes,
        "summary": {
            "total_fields_changed": len(changes),
            "fields_added": added,
            "fields_removed": removed,
            "fields_modified": modified,
        },
    }


def _current_project_id() -> int | None:
    tenant = getattr(connection, "tenant", None)
    schema = getattr(tenant, "schema_name", None)
    if not schema or schema == get_public_schema_name():
        return None
    return getattr(tenant, "pk", None)


def _client_ip(request) -> str | None:
    if request is None:
        return None
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip() or None
    return request.META.get("REMOTE_ADDR") or None


def record(
    *,
    action: str,
    instance=None,
    model_name: str | None = None,
    object_id: Any = None,
    object_repr: str | None = None,
    old_values: dict | None = None,
    new_values: dict | None = None,
    user=None,
    request=None,
    batch_id: uuid.UUID | None = None,
    project_id: int | None = None,
) -> AuditLog:
    """Append one audit record."""
    old_values = old_values or {}
    new_values = new_values or {}
    if instance is not None:
        model_name = model_name or instance.__class__.__name__
        object_id = object_id if object_id is not None else instance.pk
        object_repr = object_repr if object_repr is not None else str(instance)
        labels = _labels(instance.__class__)
    else:
        labels = {}
    details = build_change_details(old_values, new_values, labels)
    if user is None and request is not None:
        user = getattr(request, "user", None)
    if user is not None and not getattr(user, "is_authenticated", False):
        user = None
    if project_id is None:
        project_id = _current_project_id()
    organization_id = getattr(user, "organization_id", None) if user else None
    return AuditLog.objects.create(
        organization_id=organization_id,
        project_id=project_id,
        user=user,
        action=action,
        model_name=model_name or "",
        object_id=str(object_id) if object_id is not None else "",
        object_repr=(object_repr or "")[:500],
        old_values=_json_safe(old_values),
        new_values=_json_safe(new_values),
        changed_fields=details["changed_fields"],
        change_details=details,
        batch_id=batch_id,
        ip_address=_client_ip(request),
        user_agent=(request.META.get("HTTP_USER_AGENT", "") if request else "")[:500],
    )
