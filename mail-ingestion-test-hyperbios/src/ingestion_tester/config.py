from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from .scenarios import AttachmentSpec, AttachmentType, Scenario, SenderType


class ConfigError(ValueError):
    pass


def _require(value: Any, field: str) -> Any:
    if value is None or value == "":
        raise ConfigError(f"Missing required field: {field}")
    return value


def _parse_attachment(raw: dict[str, Any], index: int) -> AttachmentSpec:
    try:
        atype = AttachmentType(raw.get("type"))
    except Exception as exc:
        raise ConfigError(f"Invalid attachment type at index {index}") from exc
    filename = _require(raw.get("filename"), f"attachments[{index}].filename")
    size_kb = raw.get("size_kb")
    if not isinstance(size_kb, int) or size_kb <= 0:
        raise ConfigError(f"Invalid size_kb at index {index}")
    return AttachmentSpec(type=atype, filename=filename, size_kb=size_kb)


def _parse_scenario(raw: dict[str, Any], index: int) -> Scenario:
    try:
        sender_type = SenderType(raw.get("sender_type"))
    except Exception as exc:
        raise ConfigError(f"Invalid sender_type at scenario index {index}") from exc

    attachments_raw = raw.get("attachments") or []
    attachments = tuple(
        _parse_attachment(att, idx) for idx, att in enumerate(attachments_raw)
    )
    tags_raw = raw.get("tags") or []
    if not isinstance(tags_raw, list):
        raise ConfigError(f"Invalid tags at scenario index {index}")

    return Scenario(
        id=_require(raw.get("id"), f"scenarios[{index}].id"),
        sender_type=sender_type,
        entity_display_name=_require(
            raw.get("entity_display_name"), f"scenarios[{index}].entity_display_name"
        ),
        from_email=_require(raw.get("from_email"), f"scenarios[{index}].from_email"),
        reply_to=_require(raw.get("reply_to"), f"scenarios[{index}].reply_to"),
        subject_template=_require(
            raw.get("subject_template"), f"scenarios[{index}].subject_template"
        ),
        body_template=_require(
            raw.get("body_template"), f"scenarios[{index}].body_template"
        ),
        attachments=attachments,
        tags=tuple(tags_raw),
    )


def load_config(path: str | Path) -> list[Scenario]:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config not found: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or "scenarios" not in data:
        raise ConfigError("Invalid config: root must contain 'scenarios'")
    scenarios_raw = data["scenarios"]
    if not isinstance(scenarios_raw, list):
        raise ConfigError("Invalid config: 'scenarios' must be a list")
    scenarios = [_parse_scenario(item, idx) for idx, item in enumerate(scenarios_raw)]

    ids = [sc.id for sc in scenarios]
    if len(ids) != len(set(ids)):
        raise ConfigError("Duplicate scenario ids detected")
    return scenarios
