from __future__ import annotations

import os
from pathlib import Path
import random
import subprocess
from typing import Optional

import typer
from dotenv import load_dotenv

from .config import ConfigError, load_config
from .mailer import SmtpConfig, send_rendered_email
from .reporting import Reporter, summarize_console
from .scenarios import render_scenario, summarize_scenarios

app = typer.Typer(no_args_is_help=True)

DEFAULT_CONFIG = Path("scenarios/scenarios.yaml")


def _load_smtp_from_env() -> SmtpConfig:
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0"))
    if not host or not port:
        raise typer.BadParameter("SMTP_HOST and SMTP_PORT are required")
    return SmtpConfig(
        host=host,
        port=port,
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        starttls=os.getenv("SMTP_STARTTLS", "true").lower() == "true",
        smtp_from_real=os.getenv("SMTP_FROM_REAL"),
    )


def _local_smtp() -> SmtpConfig:
    return SmtpConfig(host="127.0.0.1", port=1025, starttls=False)


@app.command("list-scenarios")
def list_scenarios(config: Path = DEFAULT_CONFIG) -> None:
    try:
        scenarios = load_config(config)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc))
    for row in summarize_scenarios(scenarios):
        typer.echo(row)


@app.command("validate-config")
def validate_config(config: Path = DEFAULT_CONFIG) -> None:
    try:
        scenarios = load_config(config)
    except ConfigError as exc:
        raise typer.BadParameter(str(exc))
    typer.echo(f"OK: {len(scenarios)} scenarios")


@app.command("send")
def send(
    to: str = typer.Option(..., "--to"),
    scenario: str = typer.Option(..., "--scenario"),
    config: Path = DEFAULT_CONFIG,
    seed: Optional[int] = typer.Option(None, "--seed"),
) -> None:
    load_dotenv()
    scenarios = load_config(config)
    scenario_map = {sc.id: sc for sc in scenarios}
    if scenario not in scenario_map:
        raise typer.BadParameter(f"Unknown scenario: {scenario}")

    smtp = _load_smtp_from_env()
    reporter = Reporter()

    rendered = render_scenario(scenario_map[scenario], seed, index=0)
    result = send_rendered_email(rendered, to_addr=to, smtp=smtp)
    reporter.log(rendered, to_addr=to, result=result)
    summary = reporter.summarize()
    typer.echo(summarize_console(summary))


@app.command("batch")
def batch(
    to: str = typer.Option(..., "--to"),
    count: int = typer.Option(10, "--count"),
    randomize: bool = typer.Option(False, "--random"),
    seed: Optional[int] = typer.Option(None, "--seed"),
    config: Path = DEFAULT_CONFIG,
) -> None:
    load_dotenv()
    scenarios = load_config(config)
    smtp = _load_smtp_from_env()
    reporter = Reporter()

    rng = random.Random(seed)
    for idx in range(count):
        if randomize:
            sc = rng.choice(scenarios)
        else:
            sc = scenarios[idx % len(scenarios)]
        rendered = render_scenario(sc, seed, index=idx)
        result = send_rendered_email(rendered, to_addr=to, smtp=smtp)
        reporter.log(rendered, to_addr=to, result=result)

    summary = reporter.summarize()
    typer.echo(summarize_console(summary))


@app.command("local-up")
def local_up() -> None:
    subprocess.run(["docker", "compose", "up", "-d"], check=True)


@app.command("local-send")
def local_send(
    to: str = typer.Option("test@local.test", "--to"),
    scenario: str = typer.Option(..., "--scenario"),
    config: Path = DEFAULT_CONFIG,
    seed: Optional[int] = typer.Option(None, "--seed"),
) -> None:
    scenarios = load_config(config)
    scenario_map = {sc.id: sc for sc in scenarios}
    if scenario not in scenario_map:
        raise typer.BadParameter(f"Unknown scenario: {scenario}")

    smtp = _local_smtp()
    reporter = Reporter()

    rendered = render_scenario(scenario_map[scenario], seed, index=0)
    result = send_rendered_email(rendered, to_addr=to, smtp=smtp)
    reporter.log(rendered, to_addr=to, result=result)
    summary = reporter.summarize()
    typer.echo(summarize_console(summary))
