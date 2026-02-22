from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
import csv

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .scenarios import AttachmentSpec, AttachmentType


@dataclass(frozen=True)
class AttachmentContent:
    filename: str
    mime_type: str
    data: bytes


def _pdf_content(title: str, ref: str, size_kb: int) -> bytes:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    y = height - 80
    c.setFont("Helvetica", 16)
    c.drawString(80, y, title)
    c.setFont("Helvetica", 11)
    y -= 40
    lines = max(8, size_kb * 2)
    for i in range(lines):
        c.drawString(80, y, f"Reference: {ref} | Ligne {i + 1}")
        y -= 18
        if y < 80:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 80
    c.save()
    return buffer.getvalue()


def _png_content(title: str, ref: str, size_kb: int) -> bytes:
    size_factor = max(1, min(6, size_kb // 40))
    width = 300 * size_factor
    height = 180 * size_factor
    image = Image.new("RGB", (width, height), color=(245, 247, 250))
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.load_default()
    except Exception:
        font = None
    draw.text((20, 20), title, fill=(10, 10, 10), font=font)
    draw.text((20, 50), f"Ref: {ref}", fill=(80, 80, 80), font=font)
    draw.rectangle([20, 90, width - 20, height - 20], outline=(120, 120, 120), width=2)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _csv_content(ref: str, size_kb: int) -> bytes:
    buffer = BytesIO()
    wrapper = buffer
    text = []
    text.append("ref,date,amount,description")
    rows = max(3, size_kb * 5)
    for i in range(rows):
        text.append(f"{ref},{i + 1}, {100 + i}.00, Ligne {i + 1}")
    data = "\n".join(text).encode("utf-8")
    wrapper.write(data)
    return buffer.getvalue()


def generate_attachments(
    specs: tuple[AttachmentSpec, ...],
    title: str,
    ref: str,
) -> list[AttachmentContent]:
    items: list[AttachmentContent] = []
    for spec in specs:
        if spec.type == AttachmentType.PDF:
            data = _pdf_content(title, ref, spec.size_kb)
            items.append(AttachmentContent(spec.filename, "application/pdf", data))
        elif spec.type == AttachmentType.PNG:
            data = _png_content(title, ref, spec.size_kb)
            items.append(AttachmentContent(spec.filename, "image/png", data))
        elif spec.type == AttachmentType.CSV:
            data = _csv_content(ref, spec.size_kb)
            items.append(AttachmentContent(spec.filename, "text/csv", data))
        else:
            raise ValueError(f"Unsupported attachment type: {spec.type}")
    return items
