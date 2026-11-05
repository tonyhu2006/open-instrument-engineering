"""
Core engineering services (tenant schema) — §4.1.14 service layer.
"""

from __future__ import annotations

from django.db import transaction

from apps.audit import services as audit
from apps.core.exceptions import ServiceError
from apps.core.services import CrudService

from . import naming
from .models import (
    Client,
    InstrumentType,
    Loop,
    NamingConvention,
    Plant,
    PlantHierarchy,
    Site,
    Tag,
)

# §15.4 hierarchy belongs to ADM-02, instrument data to IDX (§4.2.6 prefixes).


class ClientService(CrudService):
    model = Client
    error_prefix = "ADM"


class SiteService(CrudService):
    model = Site
    error_prefix = "ADM"


class PlantService(CrudService):
    """Keeps exactly one PLANT root node per Plant (§15.4.5)."""

    model = Plant
    error_prefix = "ADM"

    def after_save(self, instance, *, creating, data):
        root = PlantHierarchy.alive.filter(plant=instance, parent__isnull=True).first()
        hierarchy = PlantHierarchyService(user=self.user, request=self.request)
        if root is None:
            hierarchy.create(
                {
                    "plant": instance,
                    "code": instance.code,
                    "name": instance.name,
                    "node_type": PlantHierarchy.NodeType.PLANT,
                    "is_active": instance.is_active,
                }
            )
        elif (root.code, root.name, root.is_active) != (
            instance.code,
            instance.name,
            instance.is_active,
        ):
            hierarchy.update(
                root,
                {
                    "code": instance.code,
                    "name": instance.name,
                    "is_active": instance.is_active,
                },
                require_version=False,
            )


class PlantHierarchyService(CrudService):
    model = PlantHierarchy
    error_prefix = "ADM"

    def before_save(self, instance, *, creating, data):
        if creating:
            return
        original = PlantHierarchy.objects.get(pk=instance.pk)
        if original.parent_id != instance.parent_id:
            raise ServiceError(
                "Use the move endpoint to change the parent of a node.",
                code="ADM_HIERARCHY_USE_MOVE",
                field="parent",
            )
        if original.plant_id != instance.plant_id and instance.parent_id is None:
            raise ServiceError(
                "The plant of a root node cannot be changed.",
                code="ADM_HIERARCHY_TYPE_LOCKED",
                field="plant",
            )
        if "node_type" in data:
            if original.node_type != instance.node_type:
                raise ServiceError(
                    "The node type of an existing node cannot be changed.",
                    code="ADM_HIERARCHY_TYPE_LOCKED",
                    field="node_type",
                )

    def before_delete(self, instance):
        if instance.parent_id is None and instance.plant_id:
            plant = Plant.alive.filter(pk=instance.plant_id).first()
            if plant is not None:
                raise ServiceError(
                    "The PLANT root node is deleted together with its Plant.",
                    code="ADM_HIERARCHY_ROOT_PROTECTED",
                )

    def move(self, node, new_parent, *, expected_row_version=None):
        """§5.4.3 move: re-parent a node (siblings stay ordered by code)."""
        with transaction.atomic():
            locked = self._lock(node)
            if expected_row_version not in (None, ""):
                self.check_row_version(locked, expected_row_version)
            if new_parent is None:
                raise ServiceError(
                    "Only AREA and UNIT nodes can be moved; they need a parent.",
                    code="ADM_HIERARCHY_MOVE_INVALID",
                    field="parent",
                )
            if new_parent.pk == locked.pk or new_parent.is_descendant_of(locked):
                raise ServiceError(
                    "A node cannot be moved below itself.",
                    code="ADM_HIERARCHY_MOVE_INVALID",
                    field="parent",
                )
            old = audit.snapshot(locked)
            locked.parent = new_parent
            self._stamp(locked, creating=False)
            self.validate(locked)
            self._persist(locked)
            # Children follow the plant of their new parent.
            for child in locked.get_descendants():
                if child.plant_id != locked.plant_id:
                    child.plant_id = locked.plant_id
                    child.save()
            self._audit("UPDATE", locked, old=old, new=audit.snapshot(locked))
        return locked


def _apply_naming(instance, *, entity_type, number_field, function_code=None):
    """IDX-01 / §15.5.5: validate against the default convention, if any."""
    convention = naming.find_convention(entity_type)
    if convention is None:
        return
    result = naming.validate_number(
        convention,
        getattr(instance, number_field),
        unit=instance.unit if instance.unit_id else None,
        entity_type=entity_type,
        function_code=function_code,
        exclude_pk=instance.pk,
    )
    if not result.valid:
        error = result.errors[0]
        raise ServiceError(
            error["message"],
            code=error["code"],
            field=number_field,
            details=result.as_dict(),
        )


class LoopService(CrudService):
    model = Loop
    error_prefix = "IDX"

    def before_save(self, instance, *, creating, data):
        if creating or "loop_tag" in data or "unit" in data:
            _apply_naming(instance, entity_type="LOOP", number_field="loop_tag")


class InstrumentTypeService(CrudService):
    model = InstrumentType
    error_prefix = "IDX"


class TagService(CrudService):
    model = Tag
    error_prefix = "IDX"

    def before_save(self, instance, *, creating, data):
        if creating or {"tag_number", "unit", "instrument_type"} & set(data):
            _apply_naming(
                instance,
                entity_type="TAG",
                number_field="tag_number",
                function_code=(
                    instance.instrument_type.code
                    if instance.instrument_type_id
                    else None
                ),
            )


class NamingConventionService(CrudService):
    model = NamingConvention
    error_prefix = "ADM"

    def before_save(self, instance, *, creating, data):
        if isinstance(instance.segment_definitions, list):
            instance.segment_definitions = {"segments": instance.segment_definitions}
        if instance.is_default:
            others = NamingConvention.alive.filter(
                entity_type=instance.entity_type, is_default=True
            ).exclude(pk=instance.pk)
            for other in others:
                old = audit.snapshot(other)
                other.is_default = False
                self._stamp(other, creating=False)
                self._persist(other)
                self._audit("UPDATE", other, old=old, new=audit.snapshot(other))

    def set_default(self, convention):
        return self.update(convention, {"is_default": True}, require_version=False)
