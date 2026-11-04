"""
Core Engineering Models (tenant schema).

Project hierarchy (§15.4): Client → Site → Plant → PlantHierarchy (MPTT:
PLANT / AREA / UNIT), plus Loop, InstrumentType, Tag and NamingConvention
(§15.5).

Every table inherits ``TenantBaseModel`` (§4.1.1 / §4.1.8): audit columns,
soft delete and ``row_version``. Unique constraints only consider live rows
(``is_deleted=False``) so codes can be reused after a soft delete, and carry
§4.2.6 business error codes.
"""

import re

import jsonschema
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from apps.core.models import TenantBaseModel

ALIVE = Q(is_deleted=False)

# =============================================================================
# Project hierarchy (§15.4.2 – §15.4.5)
# =============================================================================


class Client(TenantBaseModel):
    """Client / owner (§15.4.2). One per project (enforced by the UI)."""

    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50, help_text=_("Unique within the project"))
    contact_person = models.CharField(max_length=200, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    address = models.TextField(blank=True)

    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=ALIVE,
                name="unique_client_code",
                violation_error_code="ADM_CLIENT_CODE_DUPLICATE",
                violation_error_message=_("Client code already exists."),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Site(TenantBaseModel):
    """Site / location (§15.4.3)."""

    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="sites")
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50)
    location = models.CharField(max_length=500, blank=True)
    address = models.TextField(blank=True)
    timezone = models.CharField(max_length=50, default="UTC")

    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["client", "code"],
                condition=ALIVE,
                name="unique_site_code_per_client",
                violation_error_code="ADM_SITE_CODE_DUPLICATE",
                violation_error_message=_("Site code already exists for this client."),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Plant(TenantBaseModel):
    """Plant / process unit (§15.4.4)."""

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name="plants")
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    capacity = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Plant")
        verbose_name_plural = _("Plants")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "code"],
                condition=ALIVE,
                name="unique_plant_code_per_site",
                violation_error_code="ADM_PLANT_CODE_DUPLICATE",
                violation_error_message=_("Plant code already exists for this site."),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class PlantHierarchy(MPTTModel, TenantBaseModel):
    """PLANT → AREA → UNIT tree (§15.4.5). Instrument tags belong to a UNIT.

    ``plant`` links every node to its Plant; children inherit it from their
    parent. Each Plant has exactly one live PLANT root node.
    """

    class NodeType(models.TextChoices):
        PLANT = "PLANT", _("Plant")
        AREA = "AREA", _("Area")
        UNIT = "UNIT", _("Unit")

    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="hierarchy_nodes",
        help_text=_("Plant this node belongs to (required for PLANT roots)"),
    )
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50)
    node_type = models.CharField(max_length=10, choices=NodeType.choices)
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    VALID_CHILDREN = {
        NodeType.PLANT: [NodeType.AREA],
        NodeType.AREA: [NodeType.UNIT],
        NodeType.UNIT: [],
    }

    class MPTTMeta:
        order_insertion_by = ["code"]

    class Meta:
        verbose_name = _("Plant Hierarchy")
        verbose_name_plural = _("Plant Hierarchies")
        default_manager_name = "objects"
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "code"],
                condition=ALIVE,
                name="unique_code_per_parent",
                violation_error_code="ADM_HIERARCHY_CODE_DUPLICATE",
                violation_error_message=_("Code already exists under this parent."),
            ),
            models.UniqueConstraint(
                fields=["plant"],
                condition=Q(parent__isnull=True, is_deleted=False),
                name="unique_root_per_plant",
                violation_error_code="ADM_HIERARCHY_ROOT_DUPLICATE",
                violation_error_message=_("This plant already has a root node."),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        super().clean()
        if self.parent_id:
            parent = self.parent
            if parent.is_deleted and not self.is_deleted:
                raise ValidationError({"parent": _("Parent node has been deleted.")})
            allowed = self.VALID_CHILDREN.get(parent.node_type, [])
            if self.node_type not in allowed:
                raise ValidationError(
                    {
                        "node_type": _(
                            "A %(child)s cannot be a child of a %(parent)s. "
                            "Valid children: %(allowed)s"
                        )
                        % {
                            "child": self.node_type,
                            "parent": parent.node_type,
                            "allowed": [str(a) for a in allowed],
                        }
                    }
                )
        else:
            if self.node_type != self.NodeType.PLANT:
                raise ValidationError(
                    {"node_type": _("Only PLANT nodes can be root nodes (no parent).")}
                )
            if not self.plant_id:
                raise ValidationError(
                    {"plant": _("A PLANT root node must reference its Plant.")}
                )

    def save(self, *args, **kwargs):
        if self.parent_id:
            self.plant_id = self.parent.plant_id
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        ancestors = self.get_ancestors(include_self=True)
        return " / ".join(node.code for node in ancestors)

    def hierarchy_codes(self) -> dict:
        """Codes of site / plant / area / unit above (and including) this node."""
        codes = {}
        for node in self.get_ancestors(include_self=True):
            codes[node.node_type.lower()] = node.code
        if self.plant_id:
            codes["plant"] = self.plant.code
            codes["site"] = self.plant.site.code
        return codes


# =============================================================================
# Instrument index (simplified, pre-WP-04 — see OQ-008)
# =============================================================================


class Loop(TenantBaseModel):
    """Control loop (IDX-07). Loop number unique within a Unit (§4.1.6)."""

    class Function(models.TextChoices):
        FLOW = "F", _("Flow")
        TEMPERATURE = "T", _("Temperature")
        PRESSURE = "P", _("Pressure")
        LEVEL = "L", _("Level")
        ANALYSIS = "A", _("Analysis")
        CONTROL = "C", _("Control")
        HAND = "H", _("Hand/Manual")
        INDICATE = "I", _("Indicate")
        SAFETY = "S", _("Safety")
        OTHER = "X", _("Other")

    loop_tag = models.CharField(max_length=50, help_text=_("Loop number"))
    function = models.CharField(max_length=2, choices=Function.choices)
    suffix = models.CharField(max_length=20, blank=True)
    unit = models.ForeignKey(
        PlantHierarchy,
        on_delete=models.PROTECT,
        related_name="loops",
        limit_choices_to={"node_type": PlantHierarchy.NodeType.UNIT},
    )
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Loop")
        verbose_name_plural = _("Loops")
        ordering = ["loop_tag"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "loop_tag"],
                condition=ALIVE,
                name="unique_loop_per_unit",
                violation_error_code="IDX_LOOP_DUPLICATE",
                violation_error_message=_("Loop number already exists in this unit."),
            ),
        ]

    def __str__(self):
        return self.loop_tag

    def clean(self):
        super().clean()
        if self.unit_id and self.unit.node_type != PlantHierarchy.NodeType.UNIT:
            raise ValidationError(
                {"unit": _("Loop must be assigned to a UNIT, not a PLANT or AREA.")}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class InstrumentType(TenantBaseModel):
    """Instrument (function) type with a JSON-Schema spec template (IDX-03)."""

    class Category(models.TextChoices):
        TRANSMITTER = "TRANSMITTER", _("Transmitter")
        CONTROL_VALVE = "CONTROL_VALVE", _("Control Valve")
        SWITCH = "SWITCH", _("Switch")
        INDICATOR = "INDICATOR", _("Indicator")
        ANALYZER = "ANALYZER", _("Analyzer")
        SENSOR = "SENSOR", _("Sensor")
        CONTROLLER = "CONTROLLER", _("Controller")
        RECORDER = "RECORDER", _("Recorder")
        OTHER = "OTHER", _("Other")

    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, help_text=_("e.g. 'FT', 'TT', 'CV'"))
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.TextField(blank=True)
    schema_template = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("JSON Schema for spec_data (empty = no constraints)"),
    )
    default_spec_data = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Instrument Type")
        verbose_name_plural = _("Instrument Types")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=ALIVE,
                name="unique_instrument_type_code",
                violation_error_code="IDX_INSTRUMENT_TYPE_DUPLICATE",
                violation_error_message=_("Instrument type code already exists."),
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        super().clean()
        if self.schema_template:
            try:
                jsonschema.Draft202012Validator.check_schema(self.schema_template)
            except jsonschema.SchemaError as exc:
                raise ValidationError(
                    {"schema_template": f"Invalid JSON Schema: {exc.message}"}
                ) from exc

    def validate_spec_data(self, spec_data):
        """Validate spec_data against schema_template → (is_valid, errors)."""
        if not self.schema_template:
            return True, []
        try:
            jsonschema.validate(instance=spec_data, schema=self.schema_template)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e.message)]
        except jsonschema.SchemaError as e:
            return False, [f"Invalid schema: {e.message}"]


class Tag(TenantBaseModel):
    """Instrument tag. Tag number unique within a Unit (§4.1.6)."""

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        PENDING = "PENDING", _("Pending")
        UNDER_REVIEW = "UNDER_REVIEW", _("Under Review")

    tag_number = models.CharField(max_length=50)
    unit = models.ForeignKey(
        PlantHierarchy,
        on_delete=models.PROTECT,
        related_name="tags",
        limit_choices_to={"node_type": PlantHierarchy.NodeType.UNIT},
    )
    loop = models.ForeignKey(
        Loop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tags",
    )
    instrument_type = models.ForeignKey(
        InstrumentType, on_delete=models.PROTECT, related_name="tags"
    )
    service = models.CharField(max_length=500, blank=True)
    description = models.TextField(blank=True)
    spec_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Must conform to the instrument type's schema_template"),
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["tag_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "tag_number"],
                condition=ALIVE,
                name="unique_tag_per_unit",
                violation_error_code="IDX_TAG_DUPLICATE",
                violation_error_message=_("Tag number already exists in this unit."),
            ),
        ]

    def __str__(self):
        return self.tag_number

    def clean(self):
        super().clean()
        errors = {}
        if self.unit_id and self.unit.node_type != PlantHierarchy.NodeType.UNIT:
            errors["unit"] = _("Tag must be assigned to a UNIT, not a PLANT or AREA.")
        if self.loop_id and self.unit_id and self.loop.unit_id != self.unit_id:
            errors["loop"] = _(
                "Loop must belong to the same unit as the tag. "
                "Tag unit: %(tag)s, Loop unit: %(loop)s"
            ) % {"tag": self.unit.code, "loop": self.loop.unit.code}
        if self.instrument_type_id and self.spec_data:
            is_valid, validation_errors = self.instrument_type.validate_spec_data(
                self.spec_data
            )
            if not is_valid:
                errors["spec_data"] = _("Spec data validation failed: %(e)s") % {
                    "e": "; ".join(validation_errors)
                }
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.spec_data and self.instrument_type_id:
            self.spec_data = dict(self.instrument_type.default_spec_data or {})
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_tag(self):
        return f"{self.unit.full_path} / {self.tag_number}"


# =============================================================================
# Naming conventions (§15.5)
# =============================================================================

SEGMENT_SCHEMA = {
    "type": "object",
    "properties": {
        "segments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "type"],
                "properties": {
                    "name": {"type": "string", "pattern": "^[a-z][a-z0-9_]*$"},
                    "display_name": {"type": "string"},
                    "position": {"type": "integer", "minimum": 1},
                    "type": {
                        "enum": [
                            "hierarchy",
                            "function",
                            "equipment",
                            "sequence",
                            "custom",
                        ]
                    },
                    "source": {"type": "string"},
                    "pattern": {"type": "string"},
                    "min_length": {"type": "integer", "minimum": 0},
                    "max_length": {"type": "integer", "minimum": 1},
                    "case": {"enum": ["upper", "lower", "mixed"]},
                    "allowed_values": {"type": "array", "items": {"type": "string"}},
                    "required": {"type": "boolean"},
                    "auto_fill": {"type": "boolean"},
                    "editable": {"type": "boolean"},
                    "default": {"type": "string"},
                    "min_value": {"type": "integer"},
                    "max_value": {"type": "integer"},
                    "padding": {"type": "integer", "minimum": 0},
                    "suffix_pattern": {"type": "string"},
                    "auto_increment": {"type": "boolean"},
                },
            },
        },
        "separator": {"type": "string"},
        "case_sensitive": {"type": "boolean"},
        "prefix_source": {"enum": ["SITE", "PLANT", "AREA"]},
    },
    "additionalProperties": False,
}


class NamingConvention(TenantBaseModel):
    """Naming rule (§15.5.1). Lives in the tenant schema, so the ``project``
    of the spec is implicit (§4.1.4)."""

    class EntityType(models.TextChoices):
        TAG = "TAG", _("Tag")
        LOOP = "LOOP", _("Loop")
        CABLE = "CABLE", _("Cable")
        JUNCTION_BOX = "JUNCTION_BOX", _("Junction Box")
        TERMINAL_STRIP = "TERMINAL_STRIP", _("Terminal Strip")

    class HierarchyFormat(models.TextChoices):
        FULL = "FULL", _("Site-Plant-Area-Unit-Function-Sequence")
        NO_SITE = "NO_SITE", _("Plant-Area-Unit-Function-Sequence")
        NO_SITE_PLANT = "NO_SITE_PLANT", _("Area-Unit-Function-Sequence")
        UNIT_ONLY = "UNIT_ONLY", _("Unit-Function-Sequence")
        FLEXIBLE_PREFIX = "FLEXIBLE_PREFIX", _("XXXX-Unit-Function-Sequence")
        CUSTOM = "CUSTOM", _("Custom Regex")

    name = models.CharField(max_length=200)
    entity_type = models.CharField(
        max_length=20, choices=EntityType.choices, default=EntityType.TAG
    )
    hierarchy_format = models.CharField(
        max_length=20,
        choices=HierarchyFormat.choices,
        default=HierarchyFormat.UNIT_ONLY,
    )
    pattern = models.CharField(
        max_length=500, help_text=_("Regular expression (named groups = segments)")
    )
    pattern_template = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("e.g. {Plant}-{Unit}-{Function}-{Sequence}"),
    )
    segment_definitions = models.JSONField(default=dict, blank=True)
    separator = models.CharField(max_length=5, default="-", blank=True)
    description = models.TextField(blank=True)
    examples = models.JSONField(default=list, blank=True)
    validation_message = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    priority = models.IntegerField(
        default=100, help_text=_("Lower value = matched first")
    )

    class Meta:
        verbose_name = _("Naming Convention")
        verbose_name_plural = _("Naming Conventions")
        ordering = ["entity_type", "-is_default", "priority", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["entity_type"],
                condition=Q(is_default=True, is_deleted=False),
                name="unique_default_naming_per_entity",
                violation_error_code="ADM_NAMING_DEFAULT_DUPLICATE",
                violation_error_message=_(
                    "Only one default naming convention per entity type."
                ),
            ),
        ]

    def __str__(self):
        return self.name

    @property
    def segments(self) -> list:
        return list((self.segment_definitions or {}).get("segments", []))

    @property
    def case_sensitive(self) -> bool:
        return bool((self.segment_definitions or {}).get("case_sensitive", False))

    def compiled(self):
        flags = 0 if self.case_sensitive else re.IGNORECASE
        return re.compile(self.pattern, flags)

    def clean(self):
        super().clean()
        errors = {}
        try:
            re.compile(self.pattern or "")
        except re.error as exc:
            errors["pattern"] = _("Invalid regular expression: %(e)s") % {"e": exc}
        if not self.pattern:
            errors["pattern"] = _("Pattern is required.")
        if isinstance(self.segment_definitions, list):
            self.segment_definitions = {"segments": self.segment_definitions}
        try:
            jsonschema.validate(self.segment_definitions or {}, SEGMENT_SCHEMA)
        except jsonschema.ValidationError as exc:
            errors["segment_definitions"] = exc.message
        if not isinstance(self.examples, list):
            errors["examples"] = _("Must be a list of strings.")
        if errors:
            raise ValidationError(errors)

    def validate_tag_number(self, tag_number: str) -> tuple[bool, str]:
        """Pattern-only check → (is_valid, message)."""
        try:
            if self.compiled().fullmatch(tag_number or ""):
                return True, ""
        except re.error as exc:
            return False, f"Invalid regex pattern: {exc}"
        return False, self.validation_message or (
            f"'{tag_number}' does not match pattern {self.pattern}"
        )
