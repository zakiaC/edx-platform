from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
from typing import Iterable

from .scenarios import RenderedScenario
from .mailer import SendResult


@dataclass(frozen=True)
class RunRecord:
    timestamp: str
    to_addr: str
    scenario_id: str
    sender_type: str
    entity_display_name: str
    subject: str
    status: str
    used_fallback_from: bool


class Reporter:
    def __init__(self, out_dir: str | Path = "out") -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.log_path = self.out_dir / "run_log.jsonl"
        self.summary_path = self.out_dir / "summary.md"
        self._records: list[RunRecord] = []

    def log(self, rendered: RenderedScenario, to_addr: str, result: SendResult) -> None:
        record = RunRecord(
            timestamp=datetime.now().isoformat(timespec="seconds"),
            to_addr=to_addr,
            scenario_id=rendered.scenario.id,
            sender_type=rendered.scenario.sender_type.value,
            entity_display_name=rendered.scenario.entity_display_name,
            subject=rendered.subject,
            status=result.status,
            used_fallback_from=result.used_fallback_from,
        )
        self._records.append(record)
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record.__dict__, ensure_ascii=False) + "\n")

    def summarize(self) -> str:
        total = len(self._records)
        success = sum(1 for r in self._records if r.status.startswith("sent"))
        failures = total - success
        lines = [
            "# Summary",
            "",
            f"Total: {total}",
            f"Success: {success}",
            f"Failures: {failures}",
            "",
            "## Details",
        ]
        for rec in self._records:
            lines.append(
                f"- {rec.timestamp} | {rec.scenario_id} | {rec.sender_type} | {rec.status}"
            )
        content = "\n".join(lines) + "\n"
        self.summary_path.write_text(content, encoding="utf-8")
        return content


def summarize_console(summary_md: str) -> str:
    lines = []
    for line in summary_md.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith("##"):
            continue
        if line.strip() == "":
            continue
        lines.append(line)
    return "\n".join(lines)
