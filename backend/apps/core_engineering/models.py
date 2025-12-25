"""
Core Engineering Models - Project Hierarchy, Plant Hierarchy, Loop, InstrumentType, Tag

These models form the foundation of the instrumentation engineering system.
Data integrity is critical for engineering applications.

All models in this file are TENANT-SPECIFIC - they are stored in project schemas.
"""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
import jsonschema

from apps.core.models import TimeStampedModel


# =============================================================================
# Project Hierarchy Models (Tenant-specific)
# =============================================================================

class Client(TimeStampedModel):
    """
    Client - Owner/customer of the project.
    Stored in tenant schema - no project FK needed (implicit from schema).
    """
    
    name = models.CharField(
        max_length=300,
        help_text=_("Client/owner name"),
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Client code (e.g., 'SINOPEC', 'CNPC')"),
    )
    contact_person = models.CharField(
        max_length=200,
        blank=True,
        help_text=_("Primary contact person"),
    )
    contact_email = models.EmailField(
        blank=True,
        help_text=_("Contact email"),
    )
    contact_phone = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Contact phone"),
    )
    address = models.TextField(
        blank=True,
        help_text=_("Client address"),
    )
    
    class Meta:
        verbose_name = _("Client")
        verbose_name_plural = _("Clients")
        ordering = ["name"]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Site(TimeStampedModel):
    """
    Site - Physical location/factory site.
    Hierarchy: Client → Site
    """
    
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="sites",
        help_text=_("Client this site belongs to"),
    )
    name = models.CharField(
        max_length=300,
        help_text=_("Site name"),
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Site code (e.g., 'ZH' for Zhenhai, 'SH' for Shanghai)"),
    )
    location = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Geographic location"),
    )
    address = models.TextField(
        blank=True,
        help_text=_("Site address"),
    )
    timezone = models.CharField(
        max_length=50,
        default="UTC",
        help_text=_("Site timezone (e.g., 'Asia/Shanghai')"),
    )
    
    class Meta:
        verbose_name = _("Site")
        verbose_name_plural = _("Sites")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["client", "code"],
                name="unique_site_code_per_client",
            ),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Plant(TimeStampedModel):
    """
    Plant - Factory/process unit within a site.
    Hierarchy: Client → Site → Plant
    """
    
    site = models.ForeignKey(
        Site,
        on_delete=models.CASCADE,
        related_name="plants",
        help_text=_("Site this plant belongs to"),
    )
    name = models.CharField(
        max_length=300,
        help_text=_("Plant name (e.g., 'Ethylene Plant', 'Aromatics Unit')"),
    )
    code = models.CharField(
        max_length=50,
        help_text=_("Plant code (e.g., 'ETH', 'ARO', 'P-001')"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Plant description"),
    )
    capacity = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Plant capacity (e.g., '1000 KTPA')"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this plant is active"),
    )
    
    class Meta:
        verbose_name = _("Plant")
        verbose_name_plural = _("Plants")
        ordering = ["code"]
        constraints = [
            models.UniqueConstraint(
                fields=["site", "code"],
                name="unique_plant_code_per_site",
            ),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


# =============================================================================
# Plant Internal Hierarchy (MPTT)
# =============================================================================

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


# =============================================================================
# Naming Conventions (Tenant-specific)
# =============================================================================

class NamingConvention(TimeStampedModel):
    """
    NamingConvention - Defines tag naming rules for a project.
    Stored in tenant schema - no project FK needed (implicit from schema).
    """
    
    class HierarchyFormat(models.TextChoices):
        FULL = "FULL", _("Site-Plant-Area-Unit-Function-Sequence")
        NO_SITE = "NO_SITE", _("Plant-Area-Unit-Function-Sequence")
        NO_SITE_PLANT = "NO_SITE_PLANT", _("Area-Unit-Function-Sequence")
        UNIT_ONLY = "UNIT_ONLY", _("Unit-Function-Sequence")
        FLEXIBLE_PREFIX = "FLEXIBLE_PREFIX", _("XXXX-Unit-Function-Sequence")
        CUSTOM = "CUSTOM", _("Custom Regex")
    
    name = models.CharField(
        max_length=200,
        help_text=_("Convention name (e.g., 'ISA-5.1 Standard')"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Convention description"),
    )
    hierarchy_format = models.CharField(
        max_length=20,
        choices=HierarchyFormat.choices,
        default=HierarchyFormat.UNIT_ONLY,
        help_text=_("Hierarchy format type"),
    )
    regex_pattern = models.CharField(
        max_length=500,
        help_text=_(
            "Regex pattern for validation. "
            "Example: ^[A-Z]{2,3}-\\d{3}[A-Z]?$"
        ),
    )
    segment_definitions = models.JSONField(
        default=list,
        blank=True,
        help_text=_(
            "Segment definitions. Example: "
            "[{'name': 'function', 'type': 'letters', 'length': 2}, ...]"
        ),
    )
    example_tags = models.JSONField(
        default=list,
        blank=True,
        help_text=_("Example valid tags for this convention"),
    )
    is_default = models.BooleanField(
        default=False,
        help_text=_("Whether this is the default convention"),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this convention is active"),
    )
    
    class Meta:
        verbose_name = _("Naming Convention")
        verbose_name_plural = _("Naming Conventions")
        ordering = ["-is_default", "name"]
    
    def __str__(self):
        return self.name
    
    def validate_tag_number(self, tag_number: str) -> tuple[bool, str]:
        """Validate a tag number against this convention."""
        import re
        try:
            pattern = re.compile(self.regex_pattern)
            if pattern.match(tag_number):
                return True, ""
            else:
                return False, f"Tag number '{tag_number}' does not match pattern: {self.regex_pattern}"
        except re.error as e:
            return False, f"Invalid regex pattern: {e}"
    
    def save(self, *args, **kwargs):
        # Ensure only one default convention
        if self.is_default:
            NamingConvention.objects.filter(
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
