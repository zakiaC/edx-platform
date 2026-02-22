from __future__ import annotations

from dataclasses import dataclass
from email.message import EmailMessage
from typing import Iterable
import smtplib
import ssl

from .attachments import AttachmentContent, generate_attachments
from .scenarios import RenderedScenario


@dataclass(frozen=True)
class SmtpConfig:
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    starttls: bool = True
    smtp_from_real: str | None = None


@dataclass(frozen=True)
class SendResult:
    ok: bool
    status: str
    used_fallback_from: bool


def build_message(
    rendered: RenderedScenario,
    to_addr: str,
    simulated_from: str,
    reply_to: str,
    attachments: Iterable[AttachmentContent],
    simulated_sender_type: str,
    simulated_entity: str,
    scenario_id: str,
    fallback_from: str | None = None,
) -> EmailMessage:
    msg = EmailMessage()
    msg["To"] = to_addr
    msg["Subject"] = rendered.subject
    msg["Reply-To"] = reply_to
    msg["X-Simulated-Sender-Type"] = simulated_sender_type
    msg["X-Simulated-Entity"] = simulated_entity
    msg["X-Test-Scenario-Id"] = scenario_id

    if fallback_from:
        msg["From"] = f"\"{simulated_entity}\" <{fallback_from}>"
        body = f"Simulated-From: {simulated_from}\n{rendered.body}"
    else:
        msg["From"] = f"\"{simulated_entity}\" <{simulated_from}>"
        body = rendered.body

    msg.set_content(body)

    for att in attachments:
        maintype, subtype = att.mime_type.split("/", 1)
        msg.add_attachment(att.data, maintype=maintype, subtype=subtype, filename=att.filename)

    return msg


def _smtp_connect(config: SmtpConfig) -> smtplib.SMTP:
    client = smtplib.SMTP(config.host, config.port, timeout=30)
    if config.starttls:
        context = ssl.create_default_context()
        client.starttls(context=context)
    if config.username and config.password:
        client.login(config.username, config.password)
    return client


def send_rendered_email(
    rendered: RenderedScenario,
    to_addr: str,
    smtp: SmtpConfig,
) -> SendResult:
    attachments = generate_attachments(
        rendered.scenario.attachments,
        title=rendered.subject,
        ref=rendered.reference,
    )

    msg = build_message(
        rendered,
        to_addr=to_addr,
        simulated_from=rendered.scenario.from_email,
        reply_to=rendered.scenario.reply_to,
        attachments=attachments,
        simulated_sender_type=rendered.scenario.sender_type.value,
        simulated_entity=rendered.scenario.entity_display_name,
        scenario_id=rendered.scenario.id,
    )

    try:
        with _smtp_connect(smtp) as client:
            client.send_message(msg)
        return SendResult(ok=True, status="sent", used_fallback_from=False)
    except smtplib.SMTPResponseException as exc:
        if smtp.smtp_from_real:
            msg = build_message(
                rendered,
                to_addr=to_addr,
                simulated_from=rendered.scenario.from_email,
                reply_to=rendered.scenario.reply_to,
                attachments=attachments,
                simulated_sender_type=rendered.scenario.sender_type.value,
                simulated_entity=rendered.scenario.entity_display_name,
                scenario_id=rendered.scenario.id,
                fallback_from=smtp.smtp_from_real,
            )
            with _smtp_connect(smtp) as client:
                client.send_message(msg)
            return SendResult(ok=True, status="sent_with_fallback_from", used_fallback_from=True)
        return SendResult(ok=False, status=f"smtp_error:{exc.smtp_code}", used_fallback_from=False)
    except Exception as exc:
        return SendResult(ok=False, status=f"error:{exc}", used_fallback_from=False)
