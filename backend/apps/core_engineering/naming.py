"""
Naming convention engine — SPECIFICATION §15.5.4 / §15.5.5 / §15.5.6, IDX-01.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import Loop, NamingConvention, PlantHierarchy, Tag

# -----------------------------------------------------------------------------
# §15.5.4 preset templates
# -----------------------------------------------------------------------------


def _seg(name, seg_type, pattern, **extra):
    data = {"name": name, "type": seg_type, "pattern": pattern, "required": True}
    data.update(extra)
    return data


_FUNCTION = _seg("function", "function", "[A-Z]{1,4}", source="instrument_type.code")
_SEQUENCE = _seg(
    "sequence",
    "sequence",
    r"\d{3}[A-Z]?",
    min_value=1,
    max_value=999,
    padding=3,
    auto_increment=True,
)

PRESET_TEMPLATES = [
    {
        "code": "ISA_5_1",
        "name": "ISA standard (ISA-5.1)",
        "entity_type": "TAG",
        "hierarchy_format": "UNIT_ONLY",
        "pattern_template": "{Function}-{Sequence}{Suffix}",
        "pattern": r"^[A-Z]{1,4}-\d{3}[A-Z]?$",
        "examples": ["FT-101", "TIC-201A"],
        "segments": [_FUNCTION, _SEQUENCE],
    },
    {
        "code": "FULL_HIERARCHY",
        "name": "Full hierarchy",
        "entity_type": "TAG",
        "hierarchy_format": "FULL",
        "pattern_template": "{Site}-{Plant}-{Area}-{Unit}-{Function}-{Sequence}",
        "pattern": r"^[A-Z]{2,4}-[A-Z]{2,4}-\d{2,3}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$",
        "examples": ["ZH-ETH-100-U01-FT-001"],
        "segments": [
            _seg("site", "hierarchy", "[A-Z]{2,4}", source="site.code", auto_fill=True),
            _seg(
                "plant", "hierarchy", "[A-Z]{2,4}", source="plant.code", auto_fill=True
            ),
            _seg("area", "hierarchy", r"\d{2,3}", source="area.code", auto_fill=True),
            _seg("unit", "hierarchy", r"U\d{2}", source="unit.code", auto_fill=True),
            _FUNCTION,
            _SEQUENCE,
        ],
    },
    {
        "code": "PLANT_UNIT",
        "name": "Plant-Unit",
        "entity_type": "TAG",
        "hierarchy_format": "CUSTOM",
        "pattern_template": "{Plant}-{Unit}-{Function}-{Sequence}",
        "pattern": r"^[A-Z]{2,4}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$",
        "examples": ["ETH-U01-FT-001"],
        "segments": [
            _seg(
                "plant", "hierarchy", "[A-Z]{2,4}", source="plant.code", auto_fill=True
            ),
            _seg("unit", "hierarchy", r"U\d{2}", source="unit.code", auto_fill=True),
            _FUNCTION,
            _SEQUENCE,
        ],
    },
    {
        "code": "AREA_UNIT",
        "name": "Area-Unit",
        "entity_type": "TAG",
        "hierarchy_format": "NO_SITE_PLANT",
        "pattern_template": "{Area}-{Unit}-{Function}-{Sequence}",
        "pattern": r"^\d{2,3}-U\d{2}-[A-Z]{1,4}-\d{3}[A-Z]?$",
        "examples": ["100-U01-FT-001"],
        "segments": [
            _seg("area", "hierarchy", r"\d{2,3}", source="area.code", auto_fill=True),
            _seg("unit", "hierarchy", r"U\d{2}", source="unit.code", auto_fill=True),
            _FUNCTION,
            _SEQUENCE,
        ],
    },
    {
        "code": "SIMPLE",
        "name": "Simple",
        "entity_type": "TAG",
        "hierarchy_format": "UNIT_ONLY",
        "pattern_template": "{Function}-{Sequence}",
        "pattern": r"^[A-Z]{1,4}-\d{3}[A-Z]?$",
        "examples": ["FT-101"],
        "segments": [_FUNCTION, _SEQUENCE],
    },
    {
        "code": "CABLE",
        "name": "Cable",
        "entity_type": "CABLE",
        "hierarchy_format": "CUSTOM",
        "pattern_template": "IC-{Function}-{Sequence}-{Core}",
        "pattern": r"^IC-[A-Z]{1,4}-\d{3}-\d{2}$",
        "examples": ["IC-FT-101-01"],
        "segments": [
            _seg("prefix", "custom", "IC", default="IC"),
            _FUNCTION,
            _seg("sequence", "sequence", r"\d{3}", padding=3, auto_increment=True),
            _seg("core", "custom", r"\d{2}", default="01"),
        ],
    },
    {
        "code": "JUNCTION_BOX",
        "name": "Junction box",
        "entity_type": "JUNCTION_BOX",
        "hierarchy_format": "CUSTOM",
        "pattern_template": "JB-{Area}-{Sequence}",
        "pattern": r"^JB-\d{2,3}-\d{2}$",
        "examples": ["JB-100-01"],
        "segments": [
            _seg("prefix", "custom", "JB", default="JB"),
            _seg("area", "hierarchy", r"\d{2,3}", source="area.code", auto_fill=True),
            _seg("sequence", "sequence", r"\d{2}", padding=2, auto_increment=True),
        ],
    },
]

TEMPLATES_BY_CODE = {t["code"]: t for t in PRESET_TEMPLATES}


def template_defaults(template: dict) -> dict:
    """Model field values for a NamingConvention created from a preset."""
    return {
        "name": template["name"],
        "entity_type": template["entity_type"],
        "hierarchy_format": template["hierarchy_format"],
        "pattern": template["pattern"],
        "pattern_template": template["pattern_template"],
        "segment_definitions": {
            "segments": [
                {**seg, "position": i + 1} for i, seg in enumerate(template["segments"])
            ],
            "separator": "-",
            "case_sensitive": False,
        },
        "separator": "-",
        "examples": list(template["examples"]),
        "validation_message": (
            f"Expected format {template['pattern_template']}, "
            f"e.g. {template['examples'][0]}"
        ),
    }


# -----------------------------------------------------------------------------
# Rule lookup / validation (§15.5.5)
# -----------------------------------------------------------------------------


def find_convention(entity_type: str, convention_id=None):
    """Explicit id, else the default rule, else the highest-priority one."""
    qs = NamingConvention.alive.filter(is_active=True)
    if convention_id:
        return qs.filter(pk=convention_id).first()
    return (
        qs.filter(entity_type=entity_type)
        .order_by("-is_default", "priority", "name")
        .first()
    )


@dataclass
class NamingResult:
    valid: bool
    number: str
    segments: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    convention_id: int | None = None
    expected_pattern: str | None = None
    message: str = ""

    def as_dict(self):
        return {
            "valid": self.valid,
            "number": self.number,
            "segments": self.segments,
            "errors": self.errors,
            "naming_convention_id": self.convention_id,
            "expected_pattern": self.expected_pattern,
            "message": self.message,
        }


def _extract_segments(convention, match, number):
    groups = {k: v for k, v in match.groupdict().items() if v is not None}
    if groups:
        return groups
    names = [s["name"] for s in convention.segments]
    separator = convention.separator or "-"
    parts = number.split(separator) if separator else [number]
    if names and len(parts) == len(names):
        return dict(zip(names, parts))
    return {}


def parse_number(convention, number: str) -> NamingResult:
    result = NamingResult(
        valid=False,
        number=number,
        convention_id=convention.pk,
        expected_pattern=convention.pattern,
    )
    match = convention.compiled().fullmatch(number or "")
    if not match:
        result.errors.append(
            {
                "code": "IDX_INVALID_NAMING_SEGMENT",
                "message": convention.validation_message
                or f"'{number}' does not match {convention.pattern}",
            }
        )
        result.message = result.errors[0]["message"]
        return result
    result.valid = True
    result.segments = _extract_segments(convention, match, number)
    return result


def validate_number(
    convention,
    number: str,
    *,
    unit: PlantHierarchy | None = None,
    entity_type: str = "TAG",
    function_code: str | None = None,
    exclude_pk=None,
) -> NamingResult:
    """§15.5.5 steps 3–6: format, hierarchy consistency, uniqueness."""
    result = parse_number(convention, number)
    if not result.valid:
        return result

    seg_types = {s["name"]: s.get("type") for s in convention.segments}
    if unit is not None:
        codes = unit.hierarchy_codes()
        for name, value in result.segments.items():
            if seg_types.get(name, "hierarchy" if name in codes else None) != (
                "hierarchy"
            ):
                continue
            expected = codes.get(name)
            if expected is not None and value.upper() != str(expected).upper():
                result.errors.append(
                    {
                        "code": "IDX_NAMING_HIERARCHY_MISMATCH",
                        "field": name,
                        "message": f"Segment '{name}'='{value}' does not match "
                        f"the selected {name} '{expected}'.",
                    }
                )
    if function_code is not None and "function" in result.segments:
        if result.segments["function"].upper() != function_code.upper():
            result.errors.append(
                {
                    "code": "IDX_NAMING_FUNCTION_MISMATCH",
                    "field": "function",
                    "message": f"Function segment '{result.segments['function']}' "
                    f"does not match instrument type '{function_code}'.",
                }
            )
    for segment in convention.segments:
        allowed = segment.get("allowed_values")
        value = result.segments.get(segment["name"])
        if (
            allowed
            and value is not None
            and value.upper() not in {a.upper() for a in allowed}
        ):
            result.errors.append(
                {
                    "code": "IDX_INVALID_NAMING_SEGMENT",
                    "field": segment["name"],
                    "message": f"'{value}' is not an allowed {segment['name']}.",
                }
            )

    if unit is not None:
        model = {"TAG": Tag, "LOOP": Loop}.get(entity_type)
        if model is not None:
            field_name = "tag_number" if model is Tag else "loop_tag"
            qs = model.alive.filter(unit=unit, **{field_name: number})
            if exclude_pk:
                qs = qs.exclude(pk=exclude_pk)
            if qs.exists():
                result.errors.append(
                    {
                        "code": (
                            "IDX_TAG_DUPLICATE"
                            if model is Tag
                            else "IDX_LOOP_DUPLICATE"
                        ),
                        "message": f"'{number}' already exists in unit {unit.code}.",
                    }
                )

    result.valid = not result.errors
    result.message = result.errors[0]["message"] if result.errors else "OK"
    return result


# -----------------------------------------------------------------------------
# Auto generation (§15.5.6)
# -----------------------------------------------------------------------------


class NamingGenerationError(ValueError):
    pass


def _source_value(segment, codes, function_code):
    source = segment.get("source", "")
    if segment["type"] == "function":
        if not function_code:
            raise NamingGenerationError("An instrument type is required.")
        return function_code
    if segment["type"] == "hierarchy":
        level = source.split(".")[0] if source else segment["name"]
        value = codes.get(level)
        if value is None:
            raise NamingGenerationError(
                f"The selected unit has no {level} to fill segment '{segment['name']}'."
            )
        return value
    if segment["type"] == "equipment":
        raise NamingGenerationError(
            "Equipment segments need the Apparatus model (IDX-06), which is not "
            "implemented yet."
        )
    default = segment.get("default") or next(
        iter(segment.get("allowed_values", [])), ""
    )
    if not default and segment.get("required", True):
        raise NamingGenerationError(f"Segment '{segment['name']}' needs a value.")
    return default


def generate_number(
    convention, *, unit: PlantHierarchy, function_code: str | None
) -> dict:
    separator = convention.separator or "-"
    codes = unit.hierarchy_codes()
    segments = convention.segments
    if not segments:
        raise NamingGenerationError(
            "The naming convention has no segment definitions to generate from."
        )
    values: dict = {}
    sequence_segment = None
    for segment in sorted(segments, key=lambda s: s.get("position", 0)):
        if segment["type"] == "sequence":
            sequence_segment = segment
            values[segment["name"]] = None
            continue
        values[segment["name"]] = str(_source_value(segment, codes, function_code))
    if sequence_segment is None:
        raise NamingGenerationError("The naming convention has no sequence segment.")

    padding = int(sequence_segment.get("padding", 3))
    start = int(sequence_segment.get("min_value", 1))
    maximum = int(sequence_segment.get("max_value", 10**padding - 1))

    def compose(seq_text):
        parts = [seq_text if v is None else v for v in values.values()]
        return separator.join(parts)

    marker = "\x00SEQ\x00"
    template = compose(marker)
    prefix, _, suffix = template.partition(marker)
    model = Loop if convention.entity_type == "LOOP" else Tag
    field_name = "loop_tag" if model is Loop else "tag_number"
    existing = model.alive.filter(unit=unit, **{f"{field_name}__istartswith": prefix})
    seq_re = re.compile(
        re.escape(prefix) + r"(\d+)" + r"[A-Z]?" + re.escape(suffix) + "$",
        re.IGNORECASE,
    )
    used = 0
    for number in existing.values_list(field_name, flat=True):
        match = seq_re.match(number)
        if match:
            used = max(used, int(match.group(1)))
    next_value = max(start, used + 1)
    if next_value > maximum:
        raise NamingGenerationError("The sequence range of this unit is exhausted.")
    sequence_text = str(next_value).zfill(padding)
    number = compose(sequence_text)
    values[sequence_segment["name"]] = sequence_text
    parsed = parse_number(convention, number)
    if not parsed.valid:
        raise NamingGenerationError(
            f"Generated number '{number}' does not satisfy the convention pattern "
            f"{convention.pattern}; check the hierarchy codes."
        )
    return {
        "generated_number": number,
        "segments": values,
        "next_sequence": next_value + 1,
        "naming_convention_id": convention.pk,
    }
