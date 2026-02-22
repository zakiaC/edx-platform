from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import random
from typing import Iterable


class SenderType(str, Enum):
    BANK = "BANK"
    TAX = "TAX"
    SUPPLIER = "SUPPLIER"
    CLIENT = "CLIENT"
    LAWYER = "LAWYER"
    HR = "HR"
    INSURANCE = "INSURANCE"


class AttachmentType(str, Enum):
    PDF = "pdf"
    PNG = "png"
    CSV = "csv"


@dataclass(frozen=True)
class AttachmentSpec:
    type: AttachmentType
    filename: str
    size_kb: int


@dataclass(frozen=True)
class Scenario:
    id: str
    sender_type: SenderType
    entity_display_name: str
    from_email: str
    reply_to: str
    subject_template: str
    body_template: str
    attachments: tuple[AttachmentSpec, ...]
    tags: tuple[str, ...]


@dataclass(frozen=True)
class RenderedScenario:
    scenario: Scenario
    subject: str
    body: str
    reference: str
    date_str: str


def build_context(scenario: Scenario, seed: int | None, index: int) -> dict[str, str]:
    rng = random.Random(None if seed is None else seed + index)
    ref = f"{scenario.id}-{rng.randint(100000, 999999)}"
    date_str = datetime.now().strftime("%Y-%m-%d")
    amount = f"{rng.randint(90, 4900)},{rng.randint(0, 99):02d}"
    return {
        "date": date_str,
        "ref": ref,
        "entity": scenario.entity_display_name,
        "amount": amount,
    }


def render_scenario(scenario: Scenario, seed: int | None, index: int) -> RenderedScenario:
    ctx = build_context(scenario, seed, index)
    subject = scenario.subject_template.format(**ctx)
    body = scenario.body_template.format(**ctx)
    return RenderedScenario(
        scenario=scenario,
        subject=subject,
        body=body,
        reference=ctx["ref"],
        date_str=ctx["date"],
    )


def summarize_scenarios(scenarios: Iterable[Scenario]) -> list[str]:
    rows = []
    for sc in scenarios:
        rows.append(
            f"{sc.id}\t{sc.sender_type}\t{sc.entity_display_name}\t{', '.join(sc.tags)}"
        )
    return rows
