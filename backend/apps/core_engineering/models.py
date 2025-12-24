"""
Core Engineering Models - Plant Hierarchy, Loop, InstrumentType, Tag

These models form the foundation of the instrumentation engineering system.
Data integrity is critical for engineering applications.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
import jsonschema

from apps.core.models import TimeStampedModel


class PlantHierarchy(MPTTModel, TimeStampedModel):
    """
    Plant Hierarchy using MPTT for efficient tree operations.
    Structure: Plant -> Area -> Unit
    All instrument tags must belong to a Unit.
    """

    class NodeType(models.TextChoices):
        PLANT = "PLANT", _("Plant")
        AREA = "AREA", _("Area")
        UNIT = "UNIT", _("Unit")

    name = models.CharField(
        max_length=200,
        help_text=_("Display name of the hierarchy node"),
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Short code/identifier (e.g., 'P-001', 'A-100', 'U-110')"),
    )
    node_type = models.CharField(
        max_length=10,
        choices=NodeType.choices,
        help_text=_("Type of hierarchy node"),
    )
    parent = TreeForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        help_text=_("Parent node in the hierarchy"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of this node"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this node is active"),
    )

    class MPTTMeta:
        order_insertion_by = ["code"]

    class Meta:
        verbose_name = _("Plant Hierarchy")
        verbose_name_plural = _("Plant Hierarchies")
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "code"],
                name="unique_code_per_parent",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def clean(self):
        """Validate hierarchy rules."""
        super().clean()
        
        if self.parent:
            parent_type = self.parent.node_type
            valid_children = {
                self.NodeType.PLANT: [self.NodeType.AREA],
                self.NodeType.AREA: [self.NodeType.UNIT],
                self.NodeType.UNIT: [],
            }
            
            if self.node_type not in valid_children.get(parent_type, []):
                raise ValidationError(
                    {
                        "node_type": _(
                            f"A {self.node_type} cannot be a child of a {parent_type}. "
                            f"Valid children for {parent_type}: {valid_children.get(parent_type, [])}"
                        )
                    }
                )
        else:
            if self.node_type != self.NodeType.PLANT:
                raise ValidationError(
                    {"node_type": _("Only PLANT nodes can be root nodes (no parent).")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_path(self):
        """Return the full hierarchy path as a string."""
        ancestors = self.get_ancestors(include_self=True)
        return " / ".join([node.code for node in ancestors])


class Loop(TimeStampedModel):
    """
    Control Loop - groups related instrument tags.
    A loop contains multiple tags (e.g., FE, FT, FIC, FV for a flow loop).
    """

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

    loop_tag = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique loop identifier (e.g., 'FIC-101', 'TIC-201')"),
    )
    function = models.CharField(
        max_length=2,
        choices=Function.choices,
        help_text=_("Primary measured variable/function"),
    )
    suffix = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Loop suffix/number (e.g., '101', '201A')"),
    )
    unit = models.ForeignKey(
        PlantHierarchy,
        on_delete=models.PROTECT,
        related_name="loops",
        limit_choices_to={"node_type": PlantHierarchy.NodeType.UNIT},
        help_text=_("Unit this loop belongs to"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Loop description/service"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this loop is active"),
    )

    class Meta:
        verbose_name = _("Loop")
        verbose_name_plural = _("Loops")
        ordering = ["loop_tag"]

    def __str__(self):
        return self.loop_tag

    def clean(self):
        """Validate that unit is actually a UNIT type node."""
        super().clean()
        if self.unit and self.unit.node_type != PlantHierarchy.NodeType.UNIT:
            raise ValidationError(
                {"unit": _("Loop must be assigned to a UNIT, not a PLANT or AREA.")}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class InstrumentType(TimeStampedModel):
    """
    Instrument Type - defines the template for instrument specifications.
    The schema_template defines what fields are required for this type.
    """

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

    name = models.CharField(
        max_length=200,
        help_text=_("Full name of the instrument type"),
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text=_("Short code (e.g., 'FT', 'TT', 'CV', 'PSV')"),
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        help_text=_("Instrument category"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Description of this instrument type"),
    )
    schema_template = models.JSONField(
        default=dict,
        help_text=_(
            "JSON Schema defining the required specification fields. "
            "Example: {'type': 'object', 'properties': {'range_min': {'type': 'number'}, ...}}"
        ),
    )
    default_spec_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Default values for spec_data when creating new tags"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this instrument type is active"),
    )

    class Meta:
        verbose_name = _("Instrument Type")
        verbose_name_plural = _("Instrument Types")
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    def validate_spec_data(self, spec_data):
        """
        Validate spec_data against the schema_template.
        Returns (is_valid, errors).
        """
        if not self.schema_template:
            return True, []
        
        try:
            jsonschema.validate(instance=spec_data, schema=self.schema_template)
            return True, []
        except jsonschema.ValidationError as e:
            return False, [str(e.message)]
        except jsonschema.SchemaError as e:
            return False, [f"Invalid schema: {e.message}"]


class Tag(TimeStampedModel):
    """
    Instrument Tag - the core model representing an instrument.
    Tag Number must be unique within a Unit.
    """

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", _("Active")
        INACTIVE = "INACTIVE", _("Inactive")
        DELETED = "DELETED", _("Deleted")
        PENDING = "PENDING", _("Pending")
        UNDER_REVIEW = "UNDER_REVIEW", _("Under Review")

    tag_number = models.CharField(
        max_length=50,
        help_text=_("Instrument tag number (e.g., 'FT-101', 'TIC-201')"),
    )
    unit = models.ForeignKey(
        PlantHierarchy,
        on_delete=models.PROTECT,
        related_name="tags",
        limit_choices_to={"node_type": PlantHierarchy.NodeType.UNIT},
        help_text=_("Unit this tag belongs to (required)"),
    )
    loop = models.ForeignKey(
        Loop,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tags",
        help_text=_("Loop this tag belongs to (optional)"),
    )
    instrument_type = models.ForeignKey(
        InstrumentType,
        on_delete=models.PROTECT,
        related_name="tags",
        help_text=_("Type of instrument"),
    )
    service = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Service description (what the instrument measures/controls)"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Additional description or notes"),
    )
    spec_data = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            "Specification data. Must conform to the instrument_type's schema_template."
        ),
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_("Current status of the tag"),
    )
    revision = models.PositiveIntegerField(
        default=1,
        help_text=_("Revision number, incremented on each update"),
    )

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")
        ordering = ["tag_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["unit", "tag_number"],
                name="unique_tag_per_unit",
            ),
        ]

    def __str__(self):
        return self.tag_number

    def clean(self):
        """Validate tag data integrity."""
        super().clean()
        errors = {}

        # Validate unit is a UNIT type
        if self.unit and self.unit.node_type != PlantHierarchy.NodeType.UNIT:
            errors["unit"] = _("Tag must be assigned to a UNIT, not a PLANT or AREA.")

        # Validate loop belongs to the same unit (if loop is set)
        if self.loop and self.unit:
            if self.loop.unit_id != self.unit_id:
                errors["loop"] = _(
                    "Loop must belong to the same unit as the tag. "
                    f"Tag unit: {self.unit}, Loop unit: {self.loop.unit}"
                )

        # Validate spec_data against instrument_type schema
        if self.instrument_type and self.spec_data:
            is_valid, validation_errors = self.instrument_type.validate_spec_data(
                self.spec_data
            )
            if not is_valid:
                errors["spec_data"] = _(
                    f"Spec data validation failed: {'; '.join(validation_errors)}"
                )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        # Increment revision on update (not on create)
        if self.pk:
            self.revision += 1
        
        # Apply default spec_data from instrument_type if empty
        if not self.spec_data and self.instrument_type:
            self.spec_data = self.instrument_type.default_spec_data.copy()
        
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def full_tag(self):
        """Return the full tag identifier including unit path."""
        return f"{self.unit.full_path} / {self.tag_number}"
