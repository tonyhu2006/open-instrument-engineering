"""
Generic service layer — SPECIFICATION §4.1.14 / §4.11.2 / AGENTS.md rule 5 & 7.

Every write goes through a service so that the "five essentials" are applied
uniformly: permission (checked by the ViewSet before calling the service),
validation (``full_clean``), transaction (``atomic``), audit (``AuditLog``)
and optimistic locking (``row_version`` / 409).
"""

from __future__ import annotations

import uuid

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, models, transaction
from rest_framework import exceptions
from rest_framework.serializers import as_serializer_error

from apps.audit import services as audit

from .exceptions import ConflictError, ServiceError
from .models import AuditedModel, SoftDeleteModel, VersionedModel


def _is_error_code(code) -> bool:
    return isinstance(code, str) and code.isupper() and "_" in code


def raise_validation(exc: DjangoValidationError):
    """Convert a Django ValidationError into an API error.

    Constraint violations that carry an explicit upper-case
    ``violation_error_code`` (e.g. ``IDX_TAG_DUPLICATE``) surface as that
    business error code (§4.2.6); everything else is a VALIDATION_ERROR.
    """
    data = as_serializer_error(exc)
    code = None
    grouped = exc.error_dict if hasattr(exc, "error_dict") else {"": exc.error_list}
    for errors in grouped.values():
        for error in errors:
            if _is_error_code(getattr(error, "code", None)):
                code = error.code
                break
        if code:
            break
    if code:
        field = next(
            (k for k in data if k not in ("non_field_errors", "__all__")), None
        )
        message = next(iter(exc.messages), "Invalid data.")
        raise ServiceError(message, code=code, field=field, details=data)
    raise exceptions.ValidationError(data)


class CrudService:
    """Create / update / (soft) delete with validation, audit and locking."""

    model: type[models.Model] | None = None
    #: §4.2.6 error-code prefix for this module (e.g. "IDX", "ADM").
    error_prefix = "DATA"

    def __init__(self, *, user=None, request=None):
        self.request = request
        if user is None and request is not None:
            user = getattr(request, "user", None)
        self.user = user if getattr(user, "is_authenticated", False) else None

    # ------------------------------------------------------------------ hooks
    def before_save(self, instance, *, creating: bool, data: dict) -> None:
        """Hook: mutate/validate the instance before it is persisted."""

    def after_save(self, instance, *, creating: bool, data: dict) -> None:
        """Hook: side effects inside the same transaction."""

    # --------------------------------------------------------------- helpers
    @property
    def user_id(self):
        return getattr(self.user, "pk", None)

    def _model(self, instance=None):
        return self.model or instance.__class__

    def _stamp(self, instance, *, creating: bool):
        if isinstance(instance, AuditedModel):
            if creating:
                instance.created_by_id = self.user_id
            instance.updated_by_id = self.user_id

    def validate(self, instance):
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise_validation(exc)

    def _persist(self, instance):
        try:
            with transaction.atomic():
                instance.save()
        except DjangoValidationError as exc:
            raise_validation(exc)
        except IntegrityError as exc:
            raise ConflictError(
                "The change violates a database constraint.",
                code=f"{self.error_prefix}_INTEGRITY_ERROR",
                details={"db_error": str(exc).splitlines()[0]},
            ) from exc

    def _audit(self, action, instance, *, old=None, new=None, batch_id=None):
        audit.record(
            action=action,
            instance=instance,
            old_values=old or {},
            new_values=new or {},
            user=self.user,
            request=self.request,
            batch_id=batch_id,
        )

    def check_row_version(self, instance, expected, *, required: bool = True):
        if not isinstance(instance, VersionedModel):
            return
        if expected in (None, ""):
            if required:
                raise ServiceError(
                    "expected_row_version is required for updates (§4.1.3).",
                    code=f"{self.error_prefix}_ROW_VERSION_REQUIRED",
                    field="expected_row_version",
                )
            return
        try:
            expected_int = int(expected)
        except (TypeError, ValueError) as exc:
            raise ServiceError(
                "expected_row_version must be an integer.",
                code=f"{self.error_prefix}_ROW_VERSION_REQUIRED",
                field="expected_row_version",
            ) from exc
        if expected_int != instance.row_version:
            raise ConflictError(
                "The record was modified by someone else. Reload and retry.",
                code=f"{self.error_prefix}_ROW_VERSION_CONFLICT",
                field="expected_row_version",
                details={
                    "expected_row_version": expected_int,
                    "current_row_version": instance.row_version,
                },
            )

    def _lock(self, instance):
        model = instance.__class__
        locked = model._base_manager.select_for_update().get(pk=instance.pk)
        if isinstance(locked, SoftDeleteModel) and locked.is_deleted:
            raise exceptions.NotFound()
        return locked

    # ------------------------------------------------------------------- CRUD
    def create(self, data: dict, *, batch_id=None):
        data = dict(data)
        data.pop("expected_row_version", None)
        with transaction.atomic():
            instance = self._model()(**data)
            self._stamp(instance, creating=True)
            self.before_save(instance, creating=True, data=data)
            self.validate(instance)
            self._persist(instance)
            self.after_save(instance, creating=True, data=data)
            self._audit(
                "CREATE", instance, new=audit.snapshot(instance), batch_id=batch_id
            )
        return instance

    def update(
        self,
        instance,
        data: dict,
        *,
        expected_row_version=None,
        batch_id=None,
        require_version: bool = True,
    ):
        data = dict(data)
        if expected_row_version is None:
            expected_row_version = data.pop("expected_row_version", None)
        else:
            data.pop("expected_row_version", None)
        with transaction.atomic():
            locked = self._lock(instance)
            self.check_row_version(
                locked, expected_row_version, required=require_version
            )
            old = audit.snapshot(locked)
            for key, value in data.items():
                setattr(locked, key, value)
            self._stamp(locked, creating=False)
            self.before_save(locked, creating=False, data=data)
            self.validate(locked)
            self._persist(locked)
            self.after_save(locked, creating=False, data=data)
            self._audit(
                "UPDATE", locked, old=old, new=audit.snapshot(locked), batch_id=batch_id
            )
        return locked

    def delete(self, instance, *, expected_row_version=None, batch_id=None):
        with transaction.atomic():
            locked = self._lock(instance)
            if expected_row_version not in (None, ""):
                self.check_row_version(locked, expected_row_version)
            self.before_delete(locked)
            if isinstance(locked, SoftDeleteModel):
                self._soft_delete(locked, batch_id=batch_id or uuid.uuid4())
            else:
                old = audit.snapshot(locked)
                pk = locked.pk
                try:
                    locked.delete()
                except models.ProtectedError as exc:
                    raise ConflictError(
                        "The record is still referenced and cannot be deleted.",
                        code=f"{self.error_prefix}_DELETE_PROTECTED",
                    ) from exc
                locked.pk = pk
                self._audit("DELETE", locked, old=old, batch_id=batch_id)

    def before_delete(self, instance) -> None:
        """Hook: veto a deletion by raising."""

    # ------------------------------------------------------------ soft delete
    def _collect(self, obj, targets, nullify, blockers, seen):
        key = (obj.__class__, obj.pk)
        if key in seen:
            return
        seen.add(key)
        targets.append(obj)
        for rel in obj._meta.related_objects:
            if rel.many_to_many or not issubclass(rel.related_model, SoftDeleteModel):
                continue
            related = rel.related_model._base_manager.filter(
                **{rel.field.name: obj, "is_deleted": False}
            )
            on_delete = rel.on_delete
            if on_delete is models.CASCADE:
                for child in related:
                    self._collect(child, targets, nullify, blockers, seen)
            elif on_delete in (models.PROTECT, models.RESTRICT):
                count = related.count()
                if count:
                    label = rel.related_model.__name__
                    blockers[label] = blockers.get(label, 0) + count
            elif on_delete is models.SET_NULL:
                for child in related:
                    nullify.append((child, rel.field.name))

    def _soft_delete(self, root, *, batch_id):
        targets, nullify, blockers, seen = [], [], {}, set()
        self._collect(root, targets, nullify, blockers, seen)
        deleting = {(t.__class__, t.pk) for t in targets}
        nullify = [(c, f) for c, f in nullify if (c.__class__, c.pk) not in deleting]
        if blockers:
            raise ConflictError(
                "The record is still referenced by active data and cannot be "
                "deleted. Remove or reassign the dependent records first.",
                code=f"{self.error_prefix}_DELETE_PROTECTED",
                details={"referenced_by": blockers},
            )
        for child, field_name in nullify:
            old = audit.snapshot(child)
            setattr(child, field_name, None)
            self._stamp(child, creating=False)
            self._persist(child)
            self._audit(
                "UPDATE", child, old=old, new=audit.snapshot(child), batch_id=batch_id
            )
        for obj in targets:
            old = audit.snapshot(obj)
            obj.is_deleted = True
            self._stamp(obj, creating=False)
            self._persist(obj)
            self._audit("DELETE", obj, old=old, batch_id=batch_id)
