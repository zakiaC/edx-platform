#!/usr/bin/env python3
"""
Update the 'About' page (overview.html) + course image for all 24 AJEP courses.
Runs inside the CMS container via: python manage.py cms shell < update_ajep_descriptions.py

Usage (from host):
  ssh staging-openedx "docker exec -i tutor_local-cms-1 python manage.py cms shell" < scripts/update_ajep_descriptions.py
"""
import os
import mimetypes
from datetime import datetime

from django.core.files.base import ContentFile
from opaque_keys.edx.keys import CourseKey
from xmodule.contentstore.content import StaticContent
from xmodule.contentstore.django import contentstore
from xmodule.modulestore.django import modulestore
from xmodule.modulestore import ModuleStoreEnum

# ---------------------------------------------------------------------------
# Course descriptions par matiere et niveau
# ---------------------------------------------------------------------------

SUBJECT_NAMES = {"MATH": "Mathematiques", "FR": "Francais", "ANG": "Anglais"}
SUBJECT_ICONS = {"MATH": "", "FR": "", "ANG": ""}

LEVEL_NAMES = {
    "CM2": "CM2", "6E": "6eme", "5E": "5eme", "4E": "4eme",
    "3E": "3eme", "2NDE": "Seconde", "1ERE": "Premiere", "TERM": "Terminale",
}

LEVEL_CYCLE = {
    "CM2": "Primaire",
    "6E": "College", "5E": "College", "4E": "College", "3E": "College",
    "2NDE": "Lycee", "1ERE": "Lycee", "TERM": "Lycee",
}

LEVEL_EXAM = {
    "3E": "Brevet des colleges",
    "1ERE": "Epreuves anticipees du Bac (EAF)",
    "TERM": "Baccalaureat",
}

# Programme detaille par cours
PROGRAMS = {
    ("MATH", "CM2"): [
        ("Trimestre 1", ["Grands nombres (lire, ecrire, comparer)", "Addition et soustraction", "Droites, segments et geometrie de base", "Mesures (longueurs, masses, contenances)"]),
        ("Trimestre 2", ["Multiplication (nombres entiers et decimaux)", "Division", "Fractions simples", "Symetrie axiale"]),
        ("Trimestre 3", ["Proportionnalite (introduction)", "Perimetres et aires", "Solides (cubes, paves)", "Problemes et raisonnement"]),
    ],
    ("MATH", "6E"): [
        ("Trimestre 1", ["Nombres entiers et decimaux", "Addition et soustraction", "Droites et segments", "Tableaux et graphiques"]),
        ("Trimestre 2", ["Multiplication", "Division euclidienne", "Angles", "Symetrie axiale"]),
        ("Trimestre 3", ["Fractions", "Proportionnalite", "Perimetres et aires", "Volumes"]),
    ],
    ("MATH", "5E"): [
        ("Trimestre 1", ["Enchainements d'operations", "Nombres relatifs", "Triangles et droites remarquables", "Statistiques"]),
        ("Trimestre 2", ["Fractions (operations)", "Proportionnalite et pourcentages", "Symetrie centrale", "Angles et parallelisme"]),
        ("Trimestre 3", ["Calcul litteral (introduction)", "Aires et perimetres", "Prismes et cylindres", "Probabilites"]),
    ],
    ("MATH", "4E"): [
        ("Trimestre 1", ["Nombres relatifs (operations)", "Fractions", "Puissances", "Theoreme de Pythagore"]),
        ("Trimestre 2", ["Calcul litteral", "Equations", "Proportionnalite", "Statistiques et moyennes"]),
        ("Trimestre 3", ["Triangles (cas d'egalite)", "Translation", "Pyramides et cones", "Probabilites"]),
    ],
    ("MATH", "3E"): [
        ("Trimestre 1", ["Arithmetique (PGCD, nombres premiers)", "Calcul litteral (identites remarquables)", "Theoreme de Thales", "Statistiques"]),
        ("Trimestre 2", ["Equations et inequations", "Fonctions lineaires et affines", "Trigonometrie", "Probabilites"]),
        ("Trimestre 3", ["Systemes d'equations", "Homotheties et rotations", "Sections de solides", "Revisions Brevet"]),
    ],
    ("MATH", "2NDE"): [
        ("Trimestre 1", ["Ensembles de nombres", "Calcul algebrique", "Equations et inequations", "Vecteurs"]),
        ("Trimestre 2", ["Fonctions (generalites)", "Fonctions de reference", "Statistiques descriptives", "Probabilites"]),
        ("Trimestre 3", ["Geometrie reperee", "Variations de fonctions", "Echantillonnage", "Algorithmique"]),
    ],
    ("MATH", "1ERE"): [
        ("Trimestre 1", ["Suites numeriques", "Second degre", "Derivation", "Produit scalaire"]),
        ("Trimestre 2", ["Fonction exponentielle", "Proportions et evolutions", "Probabilites conditionnelles", "Geometrie reperee"]),
        ("Trimestre 3", ["Suites (limites)", "Applications de la derivation", "Variables aleatoires", "Revisions"]),
    ],
    ("MATH", "TERM"): [
        ("Trimestre 1", ["Suites et recurrence", "Limites de fonctions", "Continuite", "Complements de derivation"]),
        ("Trimestre 2", ["Fonction logarithme", "Integration", "Probabilites continues", "Loi normale"]),
        ("Trimestre 3", ["Geometrie dans l'espace", "Combinatoire", "Algorithmes", "Revisions Bac"]),
    ],
    ("FR", "CM2"): [
        ("Trimestre 1", ["Grammaire (nature et fonction des mots)", "Conjugaison (present, futur, imparfait)", "Lecture comprehension"]),
        ("Trimestre 2", ["Orthographe (accords, homophones)", "Conjugaison (passe compose, passe simple)", "Redaction"]),
        ("Trimestre 3", ["Vocabulaire (familles de mots, synonymes)", "Production d'ecrits", "Poesie et recit"]),
    ],
    ("FR", "6E"): [
        ("Trimestre 1", ["Le monstre aux limites de l'humain", "Grammaire (classes grammaticales, fonctions)", "Conjugaison (temps simples)"]),
        ("Trimestre 2", ["Recits d'aventures", "Recits de creation", "Orthographe et dictee", "Le verbe (temps composes)"]),
        ("Trimestre 3", ["Resister au plus fort (fables, ruses)", "La phrase complexe", "Expression ecrite (recit, description)"]),
    ],
    ("FR", "5E"): [
        ("Trimestre 1", ["Se chercher, se construire (le voyage)", "Grammaire (propositions, complements)", "Conjugaison approfondissement"]),
        ("Trimestre 2", ["Vivre en societe (famille, amis, reseaux)", "L'etre humain est-il maitre de la nature ?", "Analyse de texte"]),
        ("Trimestre 3", ["Agir sur le monde (heros et heroines)", "Argumentation (initiation)", "Expression ecrite (description, dialogue)"]),
    ],
    ("FR", "4E"): [
        ("Trimestre 1", ["Dire l'amour (poesie lyrique)", "Grammaire (voix passive, discours rapporte)", "Conjugaison (subjonctif, conditionnel)"]),
        ("Trimestre 2", ["Individu et societe (confrontation de valeurs)", "La fiction pour interroger le reel (nouvelle realiste)", "Analyse litteraire"]),
        ("Trimestre 3", ["Informer, s'informer, deformer", "La ville, lieu de tous les possibles", "Argumentation et expression ecrite"]),
    ],
    ("FR", "3E"): [
        ("Trimestre 1", ["Se raconter, se representer (autobiographie)", "Grammaire (connecteurs, implicite)", "Reecriture"]),
        ("Trimestre 2", ["Denoncer les travers de la societe (satire)", "Visions poetiques du monde", "Dictee et analyse grammaticale"]),
        ("Trimestre 3", ["Agir dans la cite (litterature engagee)", "Progres et reves scientifiques", "Revisions Brevet (redaction + dictee)"]),
    ],
    ("FR", "2NDE"): [
        ("Trimestre 1", ["Le roman et le recit (XVIIIe au XXIe)", "Grammaire avancee (enonciation, modalisation)", "Commentaire de texte (methode)"]),
        ("Trimestre 2", ["La poesie (Moyen Age au XVIIIe)", "Le theatre (XVIIe au XXIe)", "Dissertation (initiation)"]),
        ("Trimestre 3", ["La litterature d'idees (XVIe au XVIIIe)", "Contraction de texte", "Essai et oral"]),
    ],
    ("FR", "1ERE"): [
        ("Trimestre 1", ["Le roman (LaFayette a nos jours)", "La poesie (Baudelaire a nos jours)", "Commentaire litteraire"]),
        ("Trimestre 2", ["Le theatre (Moliere a Lagarce)", "La litterature d'idees (Montaigne a nos jours)", "Dissertation"]),
        ("Trimestre 3", ["Grammaire du Bac", "Contraction et essai", "Oral de francais (preparation EAF)"]),
    ],
    ("FR", "TERM"): [
        ("Trimestre 1", ["Litterature contemporaine", "Expression et argumentation avancee", "Culture litteraire"]),
        ("Trimestre 2", ["Philosophie et litterature", "Essai et dissertation approfondie", "Analyse critique"]),
        ("Trimestre 3", ["Grand oral (preparation)", "Synthese des acquis", "Revisions Bac"]),
    ],
    ("ANG", "CM2"): [
        ("Trimestre 1", ["Greetings and Introductions", "Colours, Numbers and Alphabet", "Classroom English"]),
        ("Trimestre 2", ["Family and Pets", "Food and Drinks", "Days, Months and Weather"]),
        ("Trimestre 3", ["My house", "Hobbies and Sports", "Short stories and Songs"]),
    ],
    ("ANG", "6E"): [
        ("Trimestre 1", ["Be / Have got", "Pronouns and Adjectives", "Present simple", "School life in the UK"]),
        ("Trimestre 2", ["Present continuous", "There is / There are", "Prepositions", "Daily routines"]),
        ("Trimestre 3", ["Can / Must", "Past simple (regular verbs)", "Describing people and places", "British culture"]),
    ],
    ("ANG", "5E"): [
        ("Trimestre 1", ["Past simple (irregular verbs)", "Comparatives and Superlatives", "Travel and Geography", "Reading comprehension"]),
        ("Trimestre 2", ["Future (will / going to)", "Present perfect (introduction)", "Environment", "Writing skills"]),
        ("Trimestre 3", ["Modal verbs", "Quantifiers (some, any, much, many)", "Media and Communication", "Speaking practice"]),
    ],
    ("ANG", "4E"): [
        ("Trimestre 1", ["Present perfect (for / since)", "Past continuous", "Passive voice", "The American Dream"]),
        ("Trimestre 2", ["Conditionals (0, 1, 2)", "Reported speech (introduction)", "Science and Innovation", "Debate skills"]),
        ("Trimestre 3", ["Relative clauses", "Used to", "Expressing opinions", "Multicultural societies"]),
    ],
    ("ANG", "3E"): [
        ("Trimestre 1", ["Tenses review (all tenses)", "Reported speech", "Citizenship and Engagement", "Reading and Analysis"]),
        ("Trimestre 2", ["Conditional 3", "Passive voice (advanced)", "Art and Power", "Argumentative writing"]),
        ("Trimestre 3", ["Idioms and Phrasal verbs", "Cultural landmarks (UK / US / World)", "Revisions Brevet", "Oral practice"]),
    ],
    ("ANG", "2NDE"): [
        ("Trimestre 1", ["Vivre entre generations", "Tenses consolidation", "Grammar advanced (modals, gerund, infinitive)"]),
        ("Trimestre 2", ["Les univers professionnels", "Le village, le quartier, la ville", "Comprehension orale et ecrite"]),
        ("Trimestre 3", ["Representation de soi et rapport a autrui", "Sauver la planete", "Expression ecrite et orale"]),
    ],
    ("ANG", "1ERE"): [
        ("Trimestre 1", ["Identites et echanges", "Espace prive, espace public", "Essay writing"]),
        ("Trimestre 2", ["Art et pouvoir", "Citoyennete et mondes virtuels", "Comprehension avancee"]),
        ("Trimestre 3", ["Fictions et realites", "Innovations scientifiques", "Preparation E3C / Bac"]),
    ],
    ("ANG", "TERM"): [
        ("Trimestre 1", ["Identites et echanges", "Espace prive, espace public", "Essay and Synthesis"]),
        ("Trimestre 2", ["Art et pouvoir", "Citoyennete et mondes virtuels", "Debate and Argumentation"]),
        ("Trimestre 3", ["Diversite et inclusion", "Territoire et memoire", "Revisions Bac et Grand oral"]),
    ],
}


def build_overview_html(subj, level, program):
    """Build a rich overview.html for the course about page."""
    subj_name = SUBJECT_NAMES[subj]
    level_name = LEVEL_NAMES[level]
    cycle = LEVEL_CYCLE[level]
    icon = SUBJECT_ICONS[subj]
    exam = LEVEL_EXAM.get(level, "")

    # Programme HTML
    prog_html = ""
    for trim_name, chapters in program:
        items = "".join(f'<li style="padding:4px 0;">{ch}</li>' for ch in chapters)
        prog_html += f"""
        <div style="background:#f8f9fa;border-radius:8px;padding:16px 20px;margin-bottom:12px;">
          <h4 style="margin:0 0 8px 0;color:#0965D0;">{trim_name}</h4>
          <ul style="margin:0;padding-left:20px;color:#333;">{items}</ul>
        </div>"""

    exam_section = ""
    if exam:
        exam_section = f"""
    <div style="background:linear-gradient(135deg,#0965D0,#01E8AE);border-radius:8px;padding:16px 20px;margin-top:16px;">
      <p style="color:white;margin:0;font-weight:600;">Preparation {exam} incluse</p>
    </div>"""

    html = f"""
<div style="font-family:'Raleway',Arial,sans-serif;max-width:800px;margin:0 auto;">

  <!-- Hero image -->
  <img src="/asset-v1:AJEP+{subj}-{level}+2026+type@asset+block@scolaire_hero.svg"
       alt="Soutien Scolaire AJEP"
       style="width:100%;border-radius:12px;margin-bottom:24px;" />

  <!-- Badges -->
  <div style="display:flex;gap:10px;flex-wrap:wrap;margin-bottom:20px;">
    <span style="background:#0965D0;color:white;padding:6px 16px;border-radius:20px;font-size:14px;font-weight:600;">
      {icon} {subj_name}
    </span>
    <span style="background:#0a1628;color:white;padding:6px 16px;border-radius:20px;font-size:14px;">
      {cycle} — {level_name}
    </span>
    <span style="background:#01E8AE;color:#0a1628;padding:6px 16px;border-radius:20px;font-size:14px;font-weight:600;">
      Programme officiel 2025-2026
    </span>
  </div>

  <!-- Description -->
  <h2 style="color:#0a1628;font-size:24px;margin-bottom:12px;">
    {subj_name} {level_name} — Soutien Scolaire
  </h2>
  <p style="color:#555;font-size:16px;line-height:1.7;">
    Ce cours de <strong>{subj_name.lower()}</strong> niveau <strong>{level_name}</strong>
    est concu pour accompagner les eleves tout au long de l'annee scolaire.
    Chaque trimestre couvre les chapitres du programme officiel de l'Education nationale,
    avec des exercices interactifs, des evaluations et un suivi personnalise.
  </p>
  <p style="color:#555;font-size:16px;line-height:1.7;">
    Le cours est structure en <strong>3 trimestres progressifs</strong> suivis d'une
    <strong>evaluation finale</strong> pour valider les acquis de l'annee.
    Les contenus sont adaptes au rythme de chaque eleve avec des exercices
    de difficulte croissante.
  </p>

  <!-- Programme -->
  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:16px;font-size:20px;">
    Programme de l'annee
  </h3>
  {prog_html}
  {exam_section}

  <!-- Pedagogie -->
  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:16px;font-size:20px;">
    Notre approche pedagogique
  </h3>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;">
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-size:28px;margin:0;"></p>
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Video-cours</p>
      <p style="font-size:13px;color:#666;margin:0;">Explications claires et visuelles</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-size:28px;margin:0;"></p>
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Exercices interactifs</p>
      <p style="font-size:13px;color:#666;margin:0;">QCM, problemes et cas pratiques</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-size:28px;margin:0;"></p>
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Suivi de progression</p>
      <p style="font-size:13px;color:#666;margin:0;">Tableau de bord en temps reel</p>
    </div>
    <div style="background:#f0f7ff;border-radius:8px;padding:16px;text-align:center;">
      <p style="font-size:28px;margin:0;"></p>
      <p style="font-weight:600;margin:4px 0;color:#0a1628;">Evaluations</p>
      <p style="font-size:13px;color:#666;margin:0;">Bilans trimestriels + examen final</p>
    </div>
  </div>

  <!-- Prerequis -->
  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:12px;font-size:20px;">
    Prerequis
  </h3>
  <p style="color:#555;font-size:15px;line-height:1.6;">
    Aucun prerequis particulier. Ce cours est adapte aux eleves de <strong>{level_name}</strong>
    et suit le programme officiel. Un ordinateur ou une tablette avec une connexion internet suffit.
  </p>

  <!-- Formateur -->
  <h3 style="color:#0965D0;margin-top:32px;margin-bottom:16px;font-size:20px;">
    Votre formateur
  </h3>
  <div style="display:flex;align-items:center;gap:20px;background:#f8f9fa;border-radius:12px;padding:20px;">
    <img src="/asset-v1:AJEP+{subj}-{level}+2026+type@asset+block@abdallah_semiai.jpg"
         alt="Abdallah Semiai"
         style="width:100px;height:100px;border-radius:50%;object-fit:cover;border:3px solid #0965D0;" />
    <div>
      <p style="font-size:18px;font-weight:700;color:#0a1628;margin:0 0 4px 0;">Abdallah Semiai</p>
      <p style="font-size:14px;color:#0965D0;margin:0 0 8px 0;font-weight:600;">Formateur — Academie AJEP</p>
      <p style="font-size:14px;color:#555;margin:0;line-height:1.5;">
        Formateur dedie au soutien scolaire au sein de l'association AJEP.
        Passionne par la transmission et l'accompagnement des jeunes,
        il met son expertise au service de la reussite de chaque eleve.
      </p>
    </div>
  </div>

  <!-- AJEP -->
  <div style="background:#0a1628;border-radius:12px;padding:24px;margin-top:32px;text-align:center;">
    <img src="/asset-v1:AJEP+{subj}-{level}+2026+type@asset+block@ajep_logo.png"
         alt="Logo AJEP"
         style="width:80px;height:80px;border-radius:50%;margin-bottom:12px;background:white;padding:8px;" />
    <p style="color:#01E8AE;font-size:14px;letter-spacing:1px;margin:0 0 4px 0;text-transform:uppercase;">
      Propulse par
    </p>
    <p style="color:white;font-size:22px;font-weight:700;margin:0 0 4px 0;">
      Academie AJEP
    </p>
    <p style="color:rgba(255,255,255,0.6);font-size:14px;margin:0;">
      Avenir &middot; Jeunesse &middot; Entraide &middot; Partage
    </p>
    <p style="color:rgba(255,255,255,0.4);font-size:12px;margin:8px 0 0 0;">
      Soutien scolaire pour les jeunes de Pierrefitte-sur-Seine
    </p>
  </div>
</div>
"""
    return html


# ---------------------------------------------------------------------------
# Main execution
# ---------------------------------------------------------------------------
store = modulestore()
cs = contentstore()

# Load assets
ASSETS = {}
ASSET_FILES = {
    "scolaire_hero.svg": ("/tmp/ajep_import/scolaire-hero.svg", "image/svg+xml"),
    "abdallah_semiai.jpg": ("/tmp/ajep_import/abdallah-semiai.jpg", "image/jpeg"),
    "ajep_logo.png": ("/tmp/ajep_import/ajep-logo.png", "image/png"),
}
for asset_name, (asset_path, mime) in ASSET_FILES.items():
    if os.path.exists(asset_path):
        with open(asset_path, "rb") as f:
            ASSETS[asset_name] = (f.read(), mime)
        print(f"  Asset charge: {asset_name} ({len(ASSETS[asset_name][0])} bytes)")
    else:
        print(f"  ATTENTION: {asset_name} non trouve a {asset_path}")

LEVELS_LIST = ["CM2", "6E", "5E", "4E", "3E", "2NDE", "1ERE", "TERM"]
SUBJECTS_LIST = ["MATH", "FR", "ANG"]

updated = 0
errors = 0

for level in LEVELS_LIST:
    for subj in SUBJECTS_LIST:
        code = f"{subj}-{level}"
        course_key_str = f"course-v1:AJEP+{code}+2026"
        course_key = CourseKey.from_string(course_key_str)

        course = store.get_course(course_key)
        if course is None:
            print(f"  [MISS] {course_key_str} — cours non trouve")
            errors += 1
            continue

        # 1. Upload shared assets to the course
        for asset_name, (data, mime) in ASSETS.items():
            asset_key = course_key.make_asset_key("asset", asset_name)
            content = StaticContent(asset_key, asset_name, mime, data)
            cs.save(content)

        # 2. Upload course-specific card image
        card_filename = f"card_{subj}_{level}.svg"
        card_path = f"/tmp/ajep_import/images/{card_filename}"
        if os.path.exists(card_path):
            with open(card_path, "rb") as f:
                card_data = f.read()
            card_asset_name = "course_card.svg"
            card_key = course_key.make_asset_key("asset", card_asset_name)
            card_content = StaticContent(card_key, card_asset_name, "image/svg+xml", card_data)
            cs.save(card_content)

            # Set as course image
            course.course_image = card_asset_name
            store.update_item(course, ModuleStoreEnum.UserID.mgmt_command)

        # 2. Build and save overview HTML
        program = PROGRAMS.get((subj, level), [])
        overview_html = build_overview_html(subj, level, program)

        # Save as course about > overview
        about_key = course_key.make_usage_key("about", "overview")
        try:
            about_item = store.get_item(about_key)
            about_item.data = overview_html
            store.update_item(about_item, ModuleStoreEnum.UserID.mgmt_command)
        except Exception:
            # Create it if it doesn't exist
            store.create_item(
                ModuleStoreEnum.UserID.mgmt_command,
                course_key,
                "about",
                block_id="overview",
                fields={"data": overview_html},
            )

        updated += 1
        print(f"  [OK] {course_key_str} — description + image mises a jour")

print(f"\nTermine: {updated} cours mis a jour, {errors} erreurs")
