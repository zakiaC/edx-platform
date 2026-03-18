# -*- coding: utf-8 -*-
"""
Generation de rapports PDF Qualiopi-compatible pour Mission Formations.

Deux types de documents:
1. Attestation de formation (individuelle, par apprenant)
2. Rapport de suivi de formation (par cours ou par academie)

Utilise ReportLab (disponible dans l'environnement OpenEdX).
"""
import io
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image,
)


# ── Couleurs Mission Formations ─────────────────────────────────────────────

MF_BLEU = colors.HexColor("#0965D0")
MF_VERT = colors.HexColor("#01E8AE")
MF_DARK = colors.HexColor("#0a1628")
MF_GRIS = colors.HexColor("#6b6b6b")
MF_GRIS_CLAIR = colors.HexColor("#f5f7fa")
MF_BLANC = colors.white


# ── Styles ───────────────────────────────────────────────────────────────────

def _get_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="MF_Title",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=MF_DARK,
        spaceAfter=4 * mm,
        alignment=TA_LEFT,
    ))
    styles.add(ParagraphStyle(
        name="MF_Subtitle",
        fontName="Helvetica",
        fontSize=11,
        textColor=MF_GRIS,
        spaceAfter=8 * mm,
    ))
    styles.add(ParagraphStyle(
        name="MF_Heading",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=MF_BLEU,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    ))
    styles.add(ParagraphStyle(
        name="MF_Body",
        fontName="Helvetica",
        fontSize=10,
        textColor=MF_DARK,
        leading=14,
        spaceAfter=2 * mm,
    ))
    styles.add(ParagraphStyle(
        name="MF_Small",
        fontName="Helvetica",
        fontSize=8,
        textColor=MF_GRIS,
        leading=10,
    ))
    styles.add(ParagraphStyle(
        name="MF_Center",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=MF_DARK,
        alignment=TA_CENTER,
        spaceAfter=4 * mm,
    ))
    styles.add(ParagraphStyle(
        name="MF_Footer",
        fontName="Helvetica",
        fontSize=7,
        textColor=MF_GRIS,
        alignment=TA_CENTER,
    ))
    return styles


# ── Header commun ────────────────────────────────────────────────────────────

def _build_header(styles, doc_title=""):
    """Header Mission Formations avec logo et titre."""
    elements = []

    # Logo + nom
    header_data = [[
        Paragraph("<b>M</b>", ParagraphStyle(
            name="_logo", fontName="Helvetica-Bold", fontSize=16,
            textColor=MF_BLANC, alignment=TA_CENTER,
        )),
        Paragraph(
            "<b>Academie Mission Formations</b><br/>"
            "<font size=8 color='#6b6b6b'>Organisme de formation professionnelle</font>",
            styles["MF_Body"],
        ),
        Paragraph(
            f"<font size=8 color='#6b6b6b'>{doc_title}</font><br/>"
            f"<font size=8 color='#999999'>Date : {date.today().strftime('%d/%m/%Y')}</font>",
            ParagraphStyle(name="_right", fontName="Helvetica", fontSize=8,
                           textColor=MF_GRIS, alignment=TA_RIGHT),
        ),
    ]]
    header_table = Table(header_data, colWidths=[12 * mm, 100 * mm, 58 * mm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), MF_BLEU),
        ("TEXTCOLOR", (0, 0), (0, 0), MF_BLANC),
        ("ALIGN", (0, 0), (0, 0), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (0, 0), 4),
        ("RIGHTPADDING", (0, 0), (0, 0), 4),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 4 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MF_BLEU))
    elements.append(Spacer(1, 6 * mm))
    return elements


# ── Footer commun ────────────────────────────────────────────────────────────

def _build_footer(styles):
    elements = []
    elements.append(Spacer(1, 10 * mm))
    elements.append(HRFlowable(width="100%", thickness=0.3, color=colors.HexColor("#e8e8e8")))
    elements.append(Spacer(1, 3 * mm))
    elements.append(Paragraph(
        "Academie Mission Formations — Organisme de formation professionnelle<br/>"
        "Siege social : Thiais (94) — contact@missionformations.com<br/>"
        "Document genere automatiquement — Ne constitue pas une facture",
        styles["MF_Footer"],
    ))
    return elements


# ═══════════════════════════════════════════════════════════════════════════════
# 1. ATTESTATION DE FORMATION (individuelle)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_attestation_pdf(
    learner_name,
    learner_email,
    course_name,
    course_id,
    organization="Mission Formations",
    start_date="",
    end_date="",
    duration_hours="",
    grade="",
    is_passing=False,
    certificate_id="",
):
    """
    Genere une attestation de formation PDF Qualiopi-compatible.

    Conforme aux exigences Qualiopi (indicateur 32):
    - Identification de l'organisme
    - Identification du stagiaire
    - Identification de la formation
    - Dates et duree
    - Objectifs atteints / resultats
    - Signature
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=15 * mm, bottomMargin=15 * mm,
        leftMargin=20 * mm, rightMargin=20 * mm,
    )
    styles = _get_styles()
    elements = []

    # Header
    elements.extend(_build_header(styles, "Attestation de formation"))

    # Titre
    elements.append(Paragraph("ATTESTATION DE FORMATION", styles["MF_Center"]))
    elements.append(Spacer(1, 4 * mm))

    # Bloc organisme
    elements.append(Paragraph("Organisme de formation", styles["MF_Heading"]))
    org_data = [
        ["Raison sociale", organization],
        ["Adresse", "Thiais (94)"],
        ["Contact", "contact@missionformations.com"],
    ]
    org_table = Table(org_data, colWidths=[45 * mm, 125 * mm])
    org_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MF_GRIS),
        ("TEXTCOLOR", (1, 0), (1, -1), MF_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e8e8e8")),
    ]))
    elements.append(org_table)

    # Bloc stagiaire
    elements.append(Paragraph("Stagiaire", styles["MF_Heading"]))
    learner_data = [
        ["Nom complet", learner_name],
        ["Email", learner_email],
    ]
    learner_table = Table(learner_data, colWidths=[45 * mm, 125 * mm])
    learner_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MF_GRIS),
        ("TEXTCOLOR", (1, 0), (1, -1), MF_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e8e8e8")),
    ]))
    elements.append(learner_table)

    # Bloc formation
    elements.append(Paragraph("Formation suivie", styles["MF_Heading"]))
    formation_data = [
        ["Intitule", course_name],
        ["Identifiant", course_id],
        ["Date de debut", start_date or "--"],
        ["Date de fin", end_date or "--"],
        ["Duree", f"{duration_hours}h" if duration_hours else "--"],
    ]
    formation_table = Table(formation_data, colWidths=[45 * mm, 125 * mm])
    formation_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MF_GRIS),
        ("TEXTCOLOR", (1, 0), (1, -1), MF_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e8e8e8")),
    ]))
    elements.append(formation_table)

    # Bloc resultats
    elements.append(Paragraph("Resultats", styles["MF_Heading"]))
    status_text = "Formation validee" if is_passing else "Formation non validee"
    status_color = MF_VERT if is_passing else colors.HexColor("#e74c3c")
    results_data = [
        ["Note obtenue", grade or "--"],
        ["Statut", status_text],
    ]
    if certificate_id:
        results_data.append(["N° certificat", certificate_id])
    results_table = Table(results_data, colWidths=[45 * mm, 125 * mm])
    results_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MF_GRIS),
        ("TEXTCOLOR", (1, 0), (1, -1), MF_DARK),
        ("TEXTCOLOR", (1, 1), (1, 1), status_color),
        ("FONTNAME", (1, 1), (1, 1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e8e8e8")),
    ]))
    elements.append(results_table)

    # Mention Qualiopi
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        "La presente attestation est delivree conformement aux dispositions "
        "des articles L.6353-1 et R.6353-1 du Code du travail.",
        styles["MF_Small"],
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"Fait a Thiais, le {date.today().strftime('%d/%m/%Y')}",
        styles["MF_Body"],
    ))
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        "Le Directeur de la formation<br/><br/><br/>"
        "<b>Mission Formations</b>",
        styles["MF_Body"],
    ))

    # Footer
    elements.extend(_build_footer(styles))

    doc.build(elements)
    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
# 2. RAPPORT DE SUIVI DE FORMATION (par cours/academie)
# ═══════════════════════════════════════════════════════════════════════════════

def generate_rapport_suivi_pdf(
    course_name,
    course_id,
    organization="Mission Formations",
    start_date="",
    end_date="",
    learners=None,
    stats=None,
):
    """
    Genere un rapport de suivi de formation PDF.

    Conforme Qualiopi (indicateurs 11, 17, 32):
    - Identification de la formation
    - Liste des apprenants avec progression
    - Statistiques globales
    - Taux de completion et de reussite

    Args:
        learners: list of dicts {name, email, grade, status, enrolled_date, completion_pct}
        stats: dict {total_enrolled, total_completed, completion_rate, avg_grade, pass_rate}
    """
    learners = learners or []
    stats = stats or {}
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=15 * mm, bottomMargin=15 * mm,
        leftMargin=15 * mm, rightMargin=15 * mm,
    )
    styles = _get_styles()
    elements = []

    # Header
    elements.extend(_build_header(styles, "Rapport de suivi de formation"))

    # Titre
    elements.append(Paragraph("RAPPORT DE SUIVI DE FORMATION", styles["MF_Center"]))
    elements.append(Spacer(1, 4 * mm))

    # Infos formation
    elements.append(Paragraph("Formation", styles["MF_Heading"]))
    info_data = [
        ["Intitule", course_name],
        ["Identifiant", course_id],
        ["Organisme", organization],
        ["Periode", f"{start_date or '--'} — {end_date or '--'}"],
    ]
    info_table = Table(info_data, colWidths=[40 * mm, 140 * mm])
    info_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), MF_GRIS),
        ("TEXTCOLOR", (1, 0), (1, -1), MF_DARK),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.HexColor("#e8e8e8")),
    ]))
    elements.append(info_table)

    # Statistiques globales
    elements.append(Paragraph("Statistiques globales", styles["MF_Heading"]))
    stats_data = [[
        f"{stats.get('total_enrolled', 0)}\nInscrits",
        f"{stats.get('total_completed', 0)}\nTermines",
        f"{stats.get('completion_rate', 0)}%\nCompletion",
        f"{stats.get('avg_grade', '--')}\nMoyenne",
        f"{stats.get('pass_rate', 0)}%\nReussite",
    ]]
    stats_table = Table(stats_data, colWidths=[36 * mm] * 5)
    stats_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TEXTCOLOR", (0, 0), (-1, -1), MF_BLEU),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), MF_GRIS_CLAIR),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e8e8e8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e8e8e8")),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(stats_table)

    # Tableau des apprenants
    elements.append(Paragraph("Liste des apprenants", styles["MF_Heading"]))

    if learners:
        table_data = [["Nom", "Email", "Inscrit le", "Progression", "Note", "Statut"]]
        for lr in learners:
            status_text = lr.get("status", "--")
            table_data.append([
                lr.get("name", "--"),
                lr.get("email", "--"),
                lr.get("enrolled_date", "--"),
                f"{lr.get('completion_pct', 0)}%",
                lr.get("grade", "--"),
                status_text,
            ])

        learner_table = Table(table_data, colWidths=[35 * mm, 45 * mm, 22 * mm, 22 * mm, 18 * mm, 28 * mm])
        learner_table.setStyle(TableStyle([
            # Header row
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 8),
            ("TEXTCOLOR", (0, 0), (-1, 0), MF_BLANC),
            ("BACKGROUND", (0, 0), (-1, 0), MF_BLEU),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            # Body rows
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("TEXTCOLOR", (0, 1), (-1, -1), MF_DARK),
            ("ALIGN", (3, 1), (4, -1), "CENTER"),
            # Alternating row colors
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [MF_BLANC, MF_GRIS_CLAIR]),
            # Grid
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#e8e8e8")),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#e8e8e8")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(learner_table)
    else:
        elements.append(Paragraph("Aucun apprenant inscrit.", styles["MF_Body"]))

    # Mention
    elements.append(Spacer(1, 8 * mm))
    elements.append(Paragraph(
        "Ce rapport est genere conformement aux exigences du referentiel Qualiopi "
        "(indicateurs 11, 17 et 32) et peut etre presente lors d'un audit qualite.",
        styles["MF_Small"],
    ))
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"Genere le {date.today().strftime('%d/%m/%Y')} — Academie Mission Formations",
        styles["MF_Small"],
    ))

    # Footer
    elements.extend(_build_footer(styles))

    doc.build(elements)
    return buffer.getvalue()
