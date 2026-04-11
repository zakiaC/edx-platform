#!/usr/bin/env python3
"""
Generate 24 OLX course packages for AJEP academy (8 levels x 3 subjects).
Each package is a .tar.gz ready to import via Studio > Import.

Usage:
    python3 scripts/generate_ajep_olx.py
    -> creates ajep_courses/*.tar.gz (24 files)
"""
import os
import tarfile
import textwrap
from io import BytesIO
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom.minidom import parseString

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ajep_courses")
ORG = "AJEP"
SESSION = "2026"

# ---------------------------------------------------------------------------
# Curriculum complet : 24 cours
# ---------------------------------------------------------------------------
CURRICULUM = {
    # === MATHEMATIQUES ===
    ("MATH", "CM2"): {
        "display_name": "Mathématiques CM2 — Soutien Scolaire",
        "short_description": "Grands nombres, opérations, géométrie de base et résolution de problèmes.",
        "structure": [
            ("Trimestre 1", [
                "Grands nombres (lire, écrire, comparer)",
                "Addition et soustraction",
                "Droites, segments et géométrie de base",
                "Mesures (longueurs, masses, contenances)",
            ]),
            ("Trimestre 2", [
                "Multiplication (nombres entiers et décimaux)",
                "Division",
                "Fractions simples",
                "Symétrie axiale",
            ]),
            ("Trimestre 3", [
                "Proportionnalité (introduction)",
                "Périmètres et aires",
                "Solides (cubes, pavés)",
                "Problèmes et raisonnement",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc CM2",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "6E"): {
        "display_name": "Mathématiques 6ème — Soutien Scolaire",
        "short_description": "Nombres entiers et décimaux, géométrie, fractions et proportionnalité.",
        "structure": [
            ("Trimestre 1", [
                "Nombres entiers et décimaux",
                "Addition et soustraction",
                "Droites et segments",
                "Tableaux et graphiques",
            ]),
            ("Trimestre 2", [
                "Multiplication",
                "Division euclidienne",
                "Angles",
                "Symétrie axiale",
            ]),
            ("Trimestre 3", [
                "Fractions",
                "Proportionnalité",
                "Périmètres et aires",
                "Volumes",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 6ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "5E"): {
        "display_name": "Mathématiques 5ème — Soutien Scolaire",
        "short_description": "Opérations, nombres relatifs, géométrie et statistiques.",
        "structure": [
            ("Trimestre 1", [
                "Enchaînements d'opérations",
                "Nombres relatifs",
                "Triangles et droites remarquables",
                "Statistiques",
            ]),
            ("Trimestre 2", [
                "Fractions (opérations)",
                "Proportionnalité et pourcentages",
                "Symétrie centrale",
                "Angles et parallélisme",
            ]),
            ("Trimestre 3", [
                "Calcul littéral (introduction)",
                "Aires et périmètres",
                "Prismes et cylindres",
                "Probabilités",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 5ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "4E"): {
        "display_name": "Mathématiques 4ème — Soutien Scolaire",
        "short_description": "Nombres relatifs, calcul littéral, Pythagore et statistiques.",
        "structure": [
            ("Trimestre 1", [
                "Nombres relatifs (opérations)",
                "Fractions",
                "Puissances",
                "Théorème de Pythagore",
            ]),
            ("Trimestre 2", [
                "Calcul littéral",
                "Équations",
                "Proportionnalité",
                "Statistiques et moyennes",
            ]),
            ("Trimestre 3", [
                "Triangles (cas d'égalité)",
                "Translation",
                "Pyramides et cônes",
                "Probabilités",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 4ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "3E"): {
        "display_name": "Mathématiques 3ème — Soutien Scolaire (Brevet)",
        "short_description": "Arithmétique, fonctions, trigonométrie et préparation au Brevet.",
        "structure": [
            ("Trimestre 1", [
                "Arithmétique (PGCD, nombres premiers)",
                "Calcul littéral (identités remarquables)",
                "Théorème de Thalès",
                "Statistiques",
            ]),
            ("Trimestre 2", [
                "Équations et inéquations",
                "Fonctions linéaires et affines",
                "Trigonométrie",
                "Probabilités",
            ]),
            ("Trimestre 3", [
                "Systèmes d'équations",
                "Homothéties et rotations",
                "Sections de solides",
                "Révisions Brevet",
            ]),
            ("Évaluation finale", [
                "Brevet blanc complet",
                "Correction et analyse",
                "Méthodologie de l'épreuve",
            ]),
        ],
    },
    ("MATH", "2NDE"): {
        "display_name": "Mathématiques Seconde — Soutien Scolaire",
        "short_description": "Calcul algébrique, fonctions, vecteurs et statistiques.",
        "structure": [
            ("Trimestre 1", [
                "Ensembles de nombres",
                "Calcul algébrique",
                "Équations et inéquations",
                "Vecteurs",
            ]),
            ("Trimestre 2", [
                "Fonctions (généralités)",
                "Fonctions de référence",
                "Statistiques descriptives",
                "Probabilités",
            ]),
            ("Trimestre 3", [
                "Géométrie repérée",
                "Variations de fonctions",
                "Échantillonnage",
                "Algorithmique",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "1ERE"): {
        "display_name": "Mathématiques Première — Soutien Scolaire",
        "short_description": "Suites, dérivation, exponentielle et probabilités conditionnelles.",
        "structure": [
            ("Trimestre 1", [
                "Suites numériques",
                "Second degré",
                "Dérivation",
                "Produit scalaire",
            ]),
            ("Trimestre 2", [
                "Fonction exponentielle",
                "Proportions et évolutions",
                "Probabilités conditionnelles",
                "Géométrie repérée",
            ]),
            ("Trimestre 3", [
                "Suites (limites)",
                "Applications de la dérivation",
                "Variables aléatoires",
                "Révisions",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc Première",
                "Correction et analyse",
            ]),
        ],
    },
    ("MATH", "TERM"): {
        "display_name": "Mathématiques Terminale — Soutien Scolaire (Bac)",
        "short_description": "Suites, continuité, intégration, logarithme et préparation au Bac.",
        "structure": [
            ("Trimestre 1", [
                "Suites et récurrence",
                "Limites de fonctions",
                "Continuité",
                "Compléments de dérivation",
            ]),
            ("Trimestre 2", [
                "Fonction logarithme",
                "Intégration",
                "Probabilités continues",
                "Loi normale",
            ]),
            ("Trimestre 3", [
                "Géométrie dans l'espace",
                "Combinatoire",
                "Algorithmes",
                "Révisions Bac",
            ]),
            ("Évaluation finale", [
                "Bac blanc complet",
                "Correction et analyse",
                "Méthodologie de l'épreuve",
            ]),
        ],
    },

    # === FRANCAIS ===
    ("FR", "CM2"): {
        "display_name": "Français CM2 — Soutien Scolaire",
        "short_description": "Grammaire, conjugaison, orthographe, lecture et expression écrite.",
        "structure": [
            ("Trimestre 1", [
                "Grammaire (nature et fonction des mots)",
                "Conjugaison (présent, futur, imparfait)",
                "Lecture compréhension",
            ]),
            ("Trimestre 2", [
                "Orthographe (accords, homophones)",
                "Conjugaison (passé composé, passé simple)",
                "Rédaction",
            ]),
            ("Trimestre 3", [
                "Vocabulaire (familles de mots, synonymes)",
                "Production d'écrits",
                "Poésie et récit",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc CM2",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "6E"): {
        "display_name": "Français 6ème — Soutien Scolaire",
        "short_description": "Étude de textes, grammaire, conjugaison et expression écrite.",
        "structure": [
            ("Trimestre 1", [
                "Le monstre aux limites de l'humain",
                "Grammaire (classes grammaticales, fonctions)",
                "Conjugaison (temps simples)",
            ]),
            ("Trimestre 2", [
                "Récits d'aventures",
                "Récits de création",
                "Orthographe et dictée",
                "Le verbe (temps composés)",
            ]),
            ("Trimestre 3", [
                "Résister au plus fort (fables, ruses)",
                "La phrase complexe",
                "Expression écrite (récit, description)",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 6ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "5E"): {
        "display_name": "Français 5ème — Soutien Scolaire",
        "short_description": "Littérature, grammaire approfondie et initiation à l'argumentation.",
        "structure": [
            ("Trimestre 1", [
                "Se chercher, se construire (le voyage)",
                "Grammaire (propositions, compléments)",
                "Conjugaison approfondissement",
            ]),
            ("Trimestre 2", [
                "Vivre en société (famille, amis, réseaux)",
                "L'être humain est-il maître de la nature ?",
                "Analyse de texte",
            ]),
            ("Trimestre 3", [
                "Agir sur le monde (héros et héroïnes)",
                "Argumentation (initiation)",
                "Expression écrite (description, dialogue)",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 5ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "4E"): {
        "display_name": "Français 4ème — Soutien Scolaire",
        "short_description": "Poésie lyrique, nouvelle réaliste, argumentation et analyse littéraire.",
        "structure": [
            ("Trimestre 1", [
                "Dire l'amour (poésie lyrique)",
                "Grammaire (voix passive, discours rapporté)",
                "Conjugaison (subjonctif, conditionnel)",
            ]),
            ("Trimestre 2", [
                "Individu et société (confrontation de valeurs)",
                "La fiction pour interroger le réel (nouvelle réaliste)",
                "Analyse littéraire",
            ]),
            ("Trimestre 3", [
                "Informer, s'informer, déformer",
                "La ville, lieu de tous les possibles",
                "Argumentation et expression écrite",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 4ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "3E"): {
        "display_name": "Français 3ème — Soutien Scolaire (Brevet)",
        "short_description": "Autobiographie, littérature engagée, poésie et préparation au Brevet.",
        "structure": [
            ("Trimestre 1", [
                "Se raconter, se représenter (autobiographie)",
                "Grammaire (connecteurs, implicite)",
                "Réécriture",
            ]),
            ("Trimestre 2", [
                "Dénoncer les travers de la société (satire)",
                "Visions poétiques du monde",
                "Dictée et analyse grammaticale",
            ]),
            ("Trimestre 3", [
                "Agir dans la cité (littérature engagée)",
                "Progrès et rêves scientifiques",
                "Révisions Brevet (rédaction + dictée)",
            ]),
            ("Évaluation finale", [
                "Brevet blanc complet (français)",
                "Correction et analyse",
                "Méthodologie de l'épreuve",
            ]),
        ],
    },
    ("FR", "2NDE"): {
        "display_name": "Français Seconde — Soutien Scolaire",
        "short_description": "Roman, poésie, théâtre, littérature d'idées et méthode du commentaire.",
        "structure": [
            ("Trimestre 1", [
                "Le roman et le récit (XVIIIe au XXIe)",
                "Grammaire avancée (énonciation, modalisation)",
                "Commentaire de texte (méthode)",
            ]),
            ("Trimestre 2", [
                "La poésie (Moyen Âge au XVIIIe)",
                "Le théâtre (XVIIe au XXIe)",
                "Dissertation (initiation)",
            ]),
            ("Trimestre 3", [
                "La littérature d'idées (XVIe au XVIIIe)",
                "Contraction de texte",
                "Essai et oral",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "1ERE"): {
        "display_name": "Français Première — Soutien Scolaire (EAF)",
        "short_description": "Roman, poésie, théâtre, littérature d'idées et préparation au Bac de français.",
        "structure": [
            ("Trimestre 1", [
                "Le roman (LaFayette à nos jours)",
                "La poésie (Baudelaire à nos jours)",
                "Commentaire littéraire",
            ]),
            ("Trimestre 2", [
                "Le théâtre (Molière à Lagarce)",
                "La littérature d'idées (Montaigne à nos jours)",
                "Dissertation",
            ]),
            ("Trimestre 3", [
                "Grammaire du Bac",
                "Contraction et essai",
                "Oral de français (préparation EAF)",
            ]),
            ("Évaluation finale", [
                "Bac blanc écrit",
                "Simulation oral EAF",
                "Correction et analyse",
            ]),
        ],
    },
    ("FR", "TERM"): {
        "display_name": "Français Terminale — Soutien Scolaire (Bac)",
        "short_description": "Littérature contemporaine, argumentation avancée et préparation au Grand oral.",
        "structure": [
            ("Trimestre 1", [
                "Littérature contemporaine",
                "Expression et argumentation avancée",
                "Culture littéraire",
            ]),
            ("Trimestre 2", [
                "Philosophie et littérature",
                "Essai et dissertation approfondie",
                "Analyse critique",
            ]),
            ("Trimestre 3", [
                "Grand oral (préparation)",
                "Synthèse des acquis",
                "Révisions Bac",
            ]),
            ("Évaluation finale", [
                "Bac blanc complet",
                "Simulation Grand oral",
                "Correction et analyse",
            ]),
        ],
    },

    # === ANGLAIS ===
    ("ANG", "CM2"): {
        "display_name": "Anglais CM2 — Soutien Scolaire",
        "short_description": "Bases de l'anglais : se présenter, vocabulaire quotidien et culture.",
        "structure": [
            ("Trimestre 1", [
                "Greetings and Introductions",
                "Colours, Numbers and Alphabet",
                "Classroom English",
            ]),
            ("Trimestre 2", [
                "Family and Pets",
                "Food and Drinks",
                "Days, Months and Weather",
            ]),
            ("Trimestre 3", [
                "My house",
                "Hobbies and Sports",
                "Short stories and Songs",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc CM2",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "6E"): {
        "display_name": "Anglais 6ème — Soutien Scolaire",
        "short_description": "Be/Have, present simple et continuous, vocabulaire et culture britannique.",
        "structure": [
            ("Trimestre 1", [
                "Be / Have got",
                "Pronouns and Adjectives",
                "Present simple",
                "School life in the UK",
            ]),
            ("Trimestre 2", [
                "Present continuous",
                "There is / There are",
                "Prepositions",
                "Daily routines",
            ]),
            ("Trimestre 3", [
                "Can / Must",
                "Past simple (regular verbs)",
                "Describing people and places",
                "British culture",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 6ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "5E"): {
        "display_name": "Anglais 5ème — Soutien Scolaire",
        "short_description": "Past simple, comparatifs, futur et expression orale.",
        "structure": [
            ("Trimestre 1", [
                "Past simple (irregular verbs)",
                "Comparatives and Superlatives",
                "Travel and Geography",
                "Reading comprehension",
            ]),
            ("Trimestre 2", [
                "Future (will / going to)",
                "Present perfect (introduction)",
                "Environment",
                "Writing skills",
            ]),
            ("Trimestre 3", [
                "Modal verbs",
                "Quantifiers (some, any, much, many)",
                "Media and Communication",
                "Speaking practice",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 5ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "4E"): {
        "display_name": "Anglais 4ème — Soutien Scolaire",
        "short_description": "Present perfect, conditionals, passive voice et débat.",
        "structure": [
            ("Trimestre 1", [
                "Present perfect (for / since)",
                "Past continuous",
                "Passive voice",
                "The American Dream",
            ]),
            ("Trimestre 2", [
                "Conditionals (0, 1, 2)",
                "Reported speech (introduction)",
                "Science and Innovation",
                "Debate skills",
            ]),
            ("Trimestre 3", [
                "Relative clauses",
                "Used to",
                "Expressing opinions",
                "Multicultural societies",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc 4ème",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "3E"): {
        "display_name": "Anglais 3ème — Soutien Scolaire (Brevet)",
        "short_description": "Révision des temps, reported speech, argumentation et préparation Brevet.",
        "structure": [
            ("Trimestre 1", [
                "Tenses review (all tenses)",
                "Reported speech",
                "Citizenship and Engagement",
                "Reading and Analysis",
            ]),
            ("Trimestre 2", [
                "Conditional 3",
                "Passive voice (advanced)",
                "Art and Power",
                "Argumentative writing",
            ]),
            ("Trimestre 3", [
                "Idioms and Phrasal verbs",
                "Cultural landmarks (UK / US / World)",
                "Révisions Brevet",
                "Oral practice",
            ]),
            ("Évaluation finale", [
                "Brevet blanc complet (anglais)",
                "Correction et analyse",
                "Méthodologie de l'épreuve",
            ]),
        ],
    },
    ("ANG", "2NDE"): {
        "display_name": "Anglais Seconde — Soutien Scolaire",
        "short_description": "Consolidation grammaticale, thèmes culturels et compréhension avancée.",
        "structure": [
            ("Trimestre 1", [
                "Vivre entre générations",
                "Tenses consolidation",
                "Grammar advanced (modals, gerund, infinitive)",
            ]),
            ("Trimestre 2", [
                "Les univers professionnels",
                "Le village, le quartier, la ville",
                "Compréhension orale et écrite",
            ]),
            ("Trimestre 3", [
                "Représentation de soi et rapport à autrui",
                "Sauver la planète",
                "Expression écrite et orale",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "1ERE"): {
        "display_name": "Anglais Première — Soutien Scolaire",
        "short_description": "Axes culturels, essay writing et préparation aux épreuves E3C.",
        "structure": [
            ("Trimestre 1", [
                "Identités et échanges",
                "Espace privé, espace public",
                "Essay writing",
            ]),
            ("Trimestre 2", [
                "Art et pouvoir",
                "Citoyenneté et mondes virtuels",
                "Compréhension avancée",
            ]),
            ("Trimestre 3", [
                "Fictions et réalités",
                "Innovations scientifiques",
                "Préparation E3C / Bac",
            ]),
            ("Évaluation finale", [
                "Révision complète",
                "Examen blanc Première",
                "Correction et analyse",
            ]),
        ],
    },
    ("ANG", "TERM"): {
        "display_name": "Anglais Terminale — Soutien Scolaire (Bac)",
        "short_description": "Axes culturels avancés, argumentation et préparation au Bac et Grand oral.",
        "structure": [
            ("Trimestre 1", [
                "Identités et échanges",
                "Espace privé, espace public",
                "Essay and Synthesis",
            ]),
            ("Trimestre 2", [
                "Art et pouvoir",
                "Citoyenneté et mondes virtuels",
                "Debate and Argumentation",
            ]),
            ("Trimestre 3", [
                "Diversité et inclusion",
                "Territoire et mémoire",
                "Révisions Bac et Grand oral",
            ]),
            ("Évaluation finale", [
                "Bac blanc complet (anglais)",
                "Simulation Grand oral",
                "Correction et analyse",
            ]),
        ],
    },
}

LEVELS = [
    ("CM2", "CM2"),
    ("6E", "6ème"),
    ("5E", "5ème"),
    ("4E", "4ème"),
    ("3E", "3ème"),
    ("2NDE", "Seconde"),
    ("1ERE", "Première"),
    ("TERM", "Terminale"),
]
SUBJECTS = ["MATH", "FR", "ANG"]


def _slug(text):
    """Simple slug: lowercase, replace spaces/special chars with underscores."""
    import re
    s = text.lower().strip()
    s = re.sub(r'[àáâã]', 'a', s)
    s = re.sub(r'[éèêë]', 'e', s)
    s = re.sub(r'[îï]', 'i', s)
    s = re.sub(r'[ôö]', 'o', s)
    s = re.sub(r'[ùûü]', 'u', s)
    s = re.sub(r'[ç]', 'c', s)
    s = re.sub(r'[^a-z0-9]+', '_', s)
    return s.strip('_')[:60]


def _pretty_xml(elem):
    """Return pretty-printed XML bytes."""
    rough = tostring(elem, encoding='unicode')
    dom = parseString(rough)
    return dom.toprettyxml(indent="  ", encoding="utf-8")


def _make_overview_html(display_name, short_description, structure):
    """Generate about/overview.html content."""
    sections_html = ""
    for chap_name, seqs in structure:
        items = "".join(f"<li>{s}</li>" for s in seqs)
        sections_html += f"<h3>{chap_name}</h3><ul>{items}</ul>\n"

    return textwrap.dedent(f"""\
    <section class="about">
      <h2>À propos de ce cours</h2>
      <p>{short_description}</p>
      <h2>Programme</h2>
      {sections_html}
    </section>
    """)


def generate_course_olx(subj, level_code, output_dir):
    """Generate one OLX .tar.gz for a single course."""
    key = (subj, level_code)
    cur = CURRICULUM[key]
    course_code = f"{subj}-{level_code}"
    course_key_str = f"course-v1:{ORG}+{course_code}+{SESSION}"
    run = SESSION
    display_name = cur["display_name"]
    short_desc = cur["short_description"]
    structure = cur["structure"]

    # Root directory inside the tarball
    root_dir = "course"

    # Collect all files to write: (path_in_tar, content_bytes)
    files = []

    # -- course.xml (root pointer) --
    course_root = Element("course")
    course_root.set("url_name", run)
    course_root.set("org", ORG)
    course_root.set("course", course_code)
    files.append((f"{root_dir}/course.xml", _pretty_xml(course_root)))

    # -- course/{run}.xml (course definition with chapters) --
    course_elem = Element("course")
    course_elem.set("display_name", display_name)
    course_elem.set("short_description", short_desc)
    course_elem.set("language", "fr")
    course_elem.set("start", "2026-01-01T00:00:00+00:00")

    chapter_slugs = []
    seq_data = []  # list of (chapter_slug, seq_slug, seq_display_name)

    for chap_name, sequentials in structure:
        chap_slug = _slug(chap_name)
        # Ensure unique slug
        base = chap_slug
        counter = 1
        while chap_slug in chapter_slugs:
            chap_slug = f"{base}_{counter}"
            counter += 1
        chapter_slugs.append(chap_slug)

        chap_ref = SubElement(course_elem, "chapter")
        chap_ref.set("url_name", chap_slug)

        seq_slugs_in_chap = []
        for seq_name in sequentials:
            seq_slug = _slug(seq_name)
            base_s = seq_slug
            counter_s = 1
            all_seq_slugs = [s[1] for s in seq_data] + seq_slugs_in_chap
            while seq_slug in all_seq_slugs:
                seq_slug = f"{base_s}_{counter_s}"
                counter_s += 1
            seq_slugs_in_chap.append(seq_slug)
            seq_data.append((chap_slug, seq_slug, seq_name))

    files.append((f"{root_dir}/course/{run}.xml", _pretty_xml(course_elem)))

    # -- chapter XML files --
    chap_idx = 0
    seq_idx = 0
    for chap_name, sequentials in structure:
        chap_slug = chapter_slugs[chap_idx]
        chap_elem = Element("chapter")
        chap_elem.set("display_name", chap_name)

        for seq_name in sequentials:
            _, seq_slug, _ = seq_data[seq_idx]
            seq_ref = SubElement(chap_elem, "sequential")
            seq_ref.set("url_name", seq_slug)
            seq_idx += 1

        files.append((f"{root_dir}/chapter/{chap_slug}.xml", _pretty_xml(chap_elem)))
        chap_idx += 1

    # -- sequential XML files (each with one empty vertical) --
    for _, seq_slug, seq_display in seq_data:
        seq_elem = Element("sequential")
        seq_elem.set("display_name", seq_display)

        vert_slug = f"{seq_slug}_vert"
        vert_ref = SubElement(seq_elem, "vertical")
        vert_ref.set("url_name", vert_slug)

        files.append((f"{root_dir}/sequential/{seq_slug}.xml", _pretty_xml(seq_elem)))

        # vertical with a placeholder HTML block
        vert_elem = Element("vertical")
        vert_elem.set("display_name", seq_display)

        html_slug = f"{seq_slug}_html"
        html_ref = SubElement(vert_elem, "html")
        html_ref.set("url_name", html_slug)

        files.append((f"{root_dir}/vertical/{vert_slug}.xml", _pretty_xml(vert_elem)))

        # HTML block with placeholder
        html_elem = Element("html")
        html_elem.set("display_name", seq_display)
        html_elem.set("filename", html_slug)
        files.append((f"{root_dir}/html/{html_slug}.xml", _pretty_xml(html_elem)))

        html_content = textwrap.dedent(f"""\
        <h2>{seq_display}</h2>
        <p>Contenu à venir — {display_name}</p>
        <p><em>Ce chapitre sera complété avec des vidéos, exercices interactifs et évaluations.</em></p>
        """).encode("utf-8")
        files.append((f"{root_dir}/html/{html_slug}.html", html_content))

    # -- about/overview.html --
    overview = _make_overview_html(display_name, short_desc, structure)
    files.append((f"{root_dir}/about/overview.html", overview.encode("utf-8")))

    # -- policies/{run}/policy.json --
    import json
    policy = {
        f"course/{run}": {
            "display_name": display_name,
            "short_description": short_desc,
            "language": "fr",
            "start": "2026-01-01T00:00:00+00:00",
            "enrollment_start": "2026-01-01T00:00:00+00:00",
            "catalog_visibility": "both",
            "cert_html_view_enabled": True,
        }
    }
    files.append((
        f"{root_dir}/policies/{run}/policy.json",
        json.dumps(policy, indent=2, ensure_ascii=False).encode("utf-8"),
    ))

    # -- Write tar.gz --
    tar_name = f"AJEP_{course_code}_{SESSION}.tar.gz"
    tar_path = os.path.join(output_dir, tar_name)

    with tarfile.open(tar_path, "w:gz") as tar:
        for fpath, fcontent in files:
            info = tarfile.TarInfo(name=fpath)
            info.size = len(fcontent)
            tar.addfile(info, BytesIO(fcontent))

    return tar_name


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Génération des 24 cours OLX dans {OUTPUT_DIR}/\n")

    count = 0
    for level_code, level_label in LEVELS:
        for subj in SUBJECTS:
            tar_name = generate_course_olx(subj, level_code, OUTPUT_DIR)
            key = (subj, level_code)
            print(f"  [{count+1:02d}/24] {tar_name}  — {CURRICULUM[key]['display_name']}")
            count += 1

    print(f"\nTerminé : {count} packages OLX créés dans {OUTPUT_DIR}/")
    print("\nPour importer dans Studio :")
    print("  1. Aller sur Studio > Import")
    print("  2. Sélectionner le .tar.gz du cours")
    print("  3. Cliquer sur 'Replace my course with the one above'")
    print("\nOu via API en batch :")
    print("  for f in ajep_courses/*.tar.gz; do")
    print('    curl -X POST -F "course-data=@$f" \\')
    print("      https://studio.staging.missionformations.com/api/courses/v0/import/ \\")
    print('      -H "Authorization: Bearer $TOKEN"')
    print("  done")


if __name__ == "__main__":
    main()
