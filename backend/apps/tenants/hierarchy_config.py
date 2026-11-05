"""
``ProjectTenant.hierarchy_config`` — SPECIFICATION §15.4.6.

Pure functions (no model imports) so they can be used in data migrations.
"""

from __future__ import annotations

import copy

import jsonschema

SCHEMA_VERSION = 1

LEVEL_NAMES = ("Client", "Site", "Plant", "Area", "Unit")

CONFIG_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"type": "integer", "minimum": 1},
        "template": {"enum": ["standard", "simple", "custom"]},
        "levels": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name"],
                "properties": {
                    "name": {"enum": list(LEVEL_NAMES)},
                    "required": {"type": "boolean"},
                    "default_name": {"type": "string", "maxLength": 300},
                    "default_code": {"type": "string", "maxLength": 50},
                    "allow_multiple": {"type": "boolean"},
                },
            },
        },
        "auto_create_defaults": {"type": "boolean"},
    },
}

TEMPLATES = {
    # §15.4.6 example, verbatim.
    "standard": [
        {"name": "Client", "required": True, "default_name": "客户"},
        {
            "name": "Site",
            "required": True,
            "default_name": "主厂区",
            "allow_multiple": True,
        },
        {
            "name": "Plant",
            "required": True,
            "default_name": "主装置",
            "allow_multiple": True,
        },
        {"name": "Area", "required": False, "allow_multiple": True},
        {"name": "Unit", "required": True, "allow_multiple": True},
    ],
    # Client → Site → Unit. The PlantHierarchy tree requires PLANT → AREA →
    # UNIT, so only Client and Site are auto-created (OQ-006).
    "simple": [
        {"name": "Client", "required": True, "default_name": "客户"},
        {
            "name": "Site",
            "required": True,
            "default_name": "主厂区",
            "allow_multiple": True,
        },
        {"name": "Unit", "required": True, "allow_multiple": True},
    ],
}

DEFAULT_CODES = {"Client": "CLIENT", "Site": "SITE", "Plant": "PLANT"}


def _legacy_levels(levels):
    """Older rows stored ``levels`` as a list of lowercase names."""
    converted = []
    for level in levels or []:
        if isinstance(level, str):
            name = level.strip().capitalize()
            if name in LEVEL_NAMES:
                converted.append({"name": name, "required": name != "Area"})
        elif isinstance(level, dict):
            converted.append(level)
    return converted


def normalize(config: dict | None, *, for_new_project: bool) -> dict:
    """Return a validated, fully expanded config.

    An empty config on a *new* project means the ``standard`` template with
    ``auto_create_defaults`` (§15.4.6 flow, step ②→③). An empty config on an
    existing project stays empty.
    """
    config = copy.deepcopy(config or {})
    if not config:
        if not for_new_project:
            return {}
        config = {"template": "standard", "auto_create_defaults": True}
    if "levels" in config:
        config["levels"] = _legacy_levels(config["levels"])
    template = config.get("template") or ("custom" if config.get("levels") else None)
    if template is None:
        template = "standard"
    config["template"] = template
    if template in TEMPLATES and not config.get("levels"):
        config["levels"] = copy.deepcopy(TEMPLATES[template])
    config.setdefault("levels", [])
    config.setdefault("auto_create_defaults", for_new_project)
    config["schema_version"] = SCHEMA_VERSION
    return config


def validate(config: dict) -> list[str]:
    """Return a list of validation messages (empty when valid)."""
    if config in (None, {}):
        return []
    validator = jsonschema.Draft202012Validator(CONFIG_SCHEMA)
    errors = [
        f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in validator.iter_errors(config)
    ]
    names = [level.get("name") for level in config.get("levels", [])]
    order = [n for n in LEVEL_NAMES if n in names]
    if names != order:
        errors.append(
            "levels must follow the order Client → Site → Plant → Area → Unit."
        )
    if len(set(names)) != len(names):
        errors.append("levels must not repeat.")
    return errors


def default_levels_to_create(config: dict) -> list[dict]:
    """Levels the system creates automatically (step ③): consecutive leading
    levels among Client/Site/Plant that are required and have a default name."""
    if not config.get("auto_create_defaults"):
        return []
    result = []
    for level in config.get("levels", []):
        name = level.get("name")
        if name not in DEFAULT_CODES:
            break
        if not level.get("required") or not level.get("default_name"):
            break
        result.append(
            {
                "name": name,
                "default_name": level["default_name"],
                "code": level.get("default_code") or DEFAULT_CODES[name],
            }
        )
    return result
