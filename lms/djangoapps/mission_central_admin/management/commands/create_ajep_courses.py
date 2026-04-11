"""
Management command: create the AJEP academy and its 24 courses (8 levels x 3 subjects).

Usage:
    python manage.py lms create_ajep_courses
    python manage.py lms create_ajep_courses --dry-run
"""
import logging

from django.core.management.base import BaseCommand

from opaque_keys.edx.keys import CourseKey
from xmodule.modulestore import ModuleStoreEnum
from xmodule.modulestore.django import modulestore
from xmodule.modulestore.exceptions import DuplicateCourseError

from lms.djangoapps.mission_central_admin.models import Academy, AcademyCourse

logger = logging.getLogger(__name__)

ORG = "AJEP"
SESSION = "2026"

# ---------------------------------------------------------------------------
# Programme complet : 24 cours x ~12 chapitres = ~288 chapitres
# Cle = (SUBJECT_PREFIX, LEVEL_CODE)
# ---------------------------------------------------------------------------

CURRICULUM = {
    # =====================================================================
    # MATHEMATIQUES
    # =====================================================================
    ("MATH", "CM2"): {
        "display_name": "Mathematiques CM2 — Soutien Scolaire",
        "short_description": "Grands nombres, operations, geometrie de base et resolution de problemes.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Grands nombres (lire, ecrire, comparer)",
                "Addition et soustraction",
                "Droites, segments et geometrie de base",
                "Mesures (longueurs, masses, contenances)",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Multiplication (nombres entiers et decimaux)",
                "Division",
                "Fractions simples",
                "Symetrie axiale",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Proportionnalite (introduction)",
                "Perimetres et aires",
                "Solides (cubes, paves)",
                "Problemes et raisonnement",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc CM2",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "6E"): {
        "display_name": "Mathematiques 6eme — Soutien Scolaire",
        "short_description": "Nombres entiers et decimaux, geometrie, fractions et proportionnalite.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Nombres entiers et decimaux",
                "Addition et soustraction",
                "Droites et segments",
                "Tableaux et graphiques",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Multiplication",
                "Division euclidienne",
                "Angles",
                "Symetrie axiale",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Fractions",
                "Proportionnalite",
                "Perimetres et aires",
                "Volumes",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 6eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "5E"): {
        "display_name": "Mathematiques 5eme — Soutien Scolaire",
        "short_description": "Operations, nombres relatifs, geometrie et statistiques.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Enchainements d'operations",
                "Nombres relatifs",
                "Triangles et droites remarquables",
                "Statistiques",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Fractions (operations)",
                "Proportionnalite et pourcentages",
                "Symetrie centrale",
                "Angles et parallelisme",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Calcul litteral (introduction)",
                "Aires et perimetres",
                "Prismes et cylindres",
                "Probabilites",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 5eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "4E"): {
        "display_name": "Mathematiques 4eme — Soutien Scolaire",
        "short_description": "Nombres relatifs, calcul litteral, Pythagore et statistiques.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Nombres relatifs (operations)",
                "Fractions",
                "Puissances",
                "Theoreme de Pythagore",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Calcul litteral",
                "Equations",
                "Proportionnalite",
                "Statistiques et moyennes",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Triangles (cas d'egalite)",
                "Translation",
                "Pyramides et cones",
                "Probabilites",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 4eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "3E"): {
        "display_name": "Mathematiques 3eme — Soutien Scolaire (Brevet)",
        "short_description": "Arithmetique, fonctions, trigonometrie et preparation au Brevet.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Arithmetique (PGCD, nombres premiers)",
                "Calcul litteral (identites remarquables)",
                "Theoreme de Thales",
                "Statistiques",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Equations et inequations",
                "Fonctions lineaires et affines",
                "Trigonometrie",
                "Probabilites",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Systemes d'equations",
                "Homotheties et rotations",
                "Sections de solides",
                "Revisions Brevet",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Brevet blanc complet",
                "Correction et analyse",
                "Methodologie de l'epreuve",
            ]},
        ],
    },
    ("MATH", "2NDE"): {
        "display_name": "Mathematiques Seconde — Soutien Scolaire",
        "short_description": "Calcul algebrique, fonctions, vecteurs et statistiques.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Ensembles de nombres",
                "Calcul algebrique",
                "Equations et inequations",
                "Vecteurs",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Fonctions (generalites)",
                "Fonctions de reference",
                "Statistiques descriptives",
                "Probabilites",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Geometrie reperee",
                "Variations de fonctions",
                "Echantillonnage",
                "Algorithmique",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "1ERE"): {
        "display_name": "Mathematiques Premiere — Soutien Scolaire",
        "short_description": "Suites, derivation, exponentielle et probabilites conditionnelles.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Suites numeriques",
                "Second degre",
                "Derivation",
                "Produit scalaire",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Fonction exponentielle",
                "Proportions et evolutions",
                "Probabilites conditionnelles",
                "Geometrie reperee",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Suites (limites)",
                "Applications de la derivation",
                "Variables aleatoires",
                "Revisions",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc Premiere",
                "Correction et analyse",
            ]},
        ],
    },
    ("MATH", "TERM"): {
        "display_name": "Mathematiques Terminale — Soutien Scolaire (Bac)",
        "short_description": "Suites, continuite, integration, logarithme et preparation au Bac.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Suites et recurrence",
                "Limites de fonctions",
                "Continuite",
                "Complements de derivation",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Fonction logarithme",
                "Integration",
                "Probabilites continues",
                "Loi normale",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Geometrie dans l'espace",
                "Combinatoire",
                "Algorithmes",
                "Revisions Bac",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Bac blanc complet",
                "Correction et analyse",
                "Methodologie de l'epreuve",
            ]},
        ],
    },

    # =====================================================================
    # FRANCAIS
    # =====================================================================
    ("FR", "CM2"): {
        "display_name": "Francais CM2 — Soutien Scolaire",
        "short_description": "Grammaire, conjugaison, orthographe, lecture et expression ecrite.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Grammaire (nature et fonction des mots)",
                "Conjugaison (present, futur, imparfait)",
                "Lecture comprehension",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Orthographe (accords, homophones)",
                "Conjugaison (passe compose, passe simple)",
                "Redaction",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Vocabulaire (familles de mots, synonymes)",
                "Production d'ecrits",
                "Poesie et recit",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc CM2",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "6E"): {
        "display_name": "Francais 6eme — Soutien Scolaire",
        "short_description": "Etude de textes, grammaire, conjugaison et expression ecrite.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Le monstre aux limites de l'humain",
                "Grammaire (classes grammaticales, fonctions)",
                "Conjugaison (temps simples)",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Recits d'aventures",
                "Recits de creation",
                "Orthographe et dictee",
                "Le verbe (temps composes)",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Resister au plus fort (fables, ruses)",
                "La phrase complexe",
                "Expression ecrite (recit, description)",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 6eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "5E"): {
        "display_name": "Francais 5eme — Soutien Scolaire",
        "short_description": "Litterature, grammaire approfondie et initiation a l'argumentation.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Se chercher, se construire (le voyage)",
                "Grammaire (propositions, complements)",
                "Conjugaison approfondissement",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Vivre en societe (famille, amis, reseaux)",
                "L'etre humain est-il maitre de la nature ?",
                "Analyse de texte",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Agir sur le monde (heros et heroines)",
                "Argumentation (initiation)",
                "Expression ecrite (description, dialogue)",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 5eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "4E"): {
        "display_name": "Francais 4eme — Soutien Scolaire",
        "short_description": "Poesie lyrique, nouvelle realiste, argumentation et analyse litteraire.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Dire l'amour (poesie lyrique)",
                "Grammaire (voix passive, discours rapporte)",
                "Conjugaison (subjonctif, conditionnel)",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Individu et societe (confrontation de valeurs)",
                "La fiction pour interroger le reel (nouvelle realiste)",
                "Analyse litteraire",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Informer, s'informer, deformer",
                "La ville, lieu de tous les possibles",
                "Argumentation et expression ecrite",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 4eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "3E"): {
        "display_name": "Francais 3eme — Soutien Scolaire (Brevet)",
        "short_description": "Autobiographie, litterature engagee, poesie et preparation au Brevet.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Se raconter, se representer (autobiographie)",
                "Grammaire (connecteurs, implicite)",
                "Reecriture",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Denoncer les travers de la societe (satire)",
                "Visions poetiques du monde",
                "Dictee et analyse grammaticale",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Agir dans la cite (litterature engagee)",
                "Progres et reves scientifiques",
                "Revisions Brevet (redaction + dictee)",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Brevet blanc complet (francais)",
                "Correction et analyse",
                "Methodologie de l'epreuve",
            ]},
        ],
    },
    ("FR", "2NDE"): {
        "display_name": "Francais Seconde — Soutien Scolaire",
        "short_description": "Roman, poesie, theatre, litterature d'idees et methode du commentaire.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Le roman et le recit (XVIIIe au XXIe)",
                "Grammaire avancee (enonciation, modalisation)",
                "Commentaire de texte (methode)",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "La poesie (Moyen Age au XVIIIe)",
                "Le theatre (XVIIe au XXIe)",
                "Dissertation (initiation)",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "La litterature d'idees (XVIe au XVIIIe)",
                "Contraction de texte",
                "Essai et oral",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "1ERE"): {
        "display_name": "Francais Premiere — Soutien Scolaire (EAF)",
        "short_description": "Roman, poesie, theatre, litterature d'idees et preparation au Bac de francais.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Le roman (LaFayette a nos jours)",
                "La poesie (Baudelaire a nos jours)",
                "Commentaire litteraire",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Le theatre (Moliere a Lagarce)",
                "La litterature d'idees (Montaigne a nos jours)",
                "Dissertation",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Grammaire du Bac",
                "Contraction et essai",
                "Oral de francais (preparation EAF)",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Bac blanc ecrit",
                "Simulation oral EAF",
                "Correction et analyse",
            ]},
        ],
    },
    ("FR", "TERM"): {
        "display_name": "Francais Terminale — Soutien Scolaire (Bac)",
        "short_description": "Litterature contemporaine, argumentation avancee et preparation au Grand oral.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Litterature contemporaine",
                "Expression et argumentation avancee",
                "Culture litteraire",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Philosophie et litterature",
                "Essai et dissertation approfondie",
                "Analyse critique",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Grand oral (preparation)",
                "Synthese des acquis",
                "Revisions Bac",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Bac blanc complet",
                "Simulation Grand oral",
                "Correction et analyse",
            ]},
        ],
    },

    # =====================================================================
    # ANGLAIS
    # =====================================================================
    ("ANG", "CM2"): {
        "display_name": "Anglais CM2 — Soutien Scolaire",
        "short_description": "Bases de l'anglais : se presenter, vocabulaire quotidien et culture.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Greetings and Introductions",
                "Colours, Numbers and Alphabet",
                "Classroom English",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Family and Pets",
                "Food and Drinks",
                "Days, Months and Weather",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "My house",
                "Hobbies and Sports",
                "Short stories and Songs",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc CM2",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "6E"): {
        "display_name": "Anglais 6eme — Soutien Scolaire",
        "short_description": "Be/Have, present simple et continuous, vocabulaire et culture britannique.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Be / Have got",
                "Pronouns and Adjectives",
                "Present simple",
                "School life in the UK",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Present continuous",
                "There is / There are",
                "Prepositions",
                "Daily routines",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Can / Must",
                "Past simple (regular verbs)",
                "Describing people and places",
                "British culture",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 6eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "5E"): {
        "display_name": "Anglais 5eme — Soutien Scolaire",
        "short_description": "Past simple, comparatifs, futur et expression orale.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Past simple (irregular verbs)",
                "Comparatives and Superlatives",
                "Travel and Geography",
                "Reading comprehension",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Future (will / going to)",
                "Present perfect (introduction)",
                "Environment",
                "Writing skills",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Modal verbs",
                "Quantifiers (some, any, much, many)",
                "Media and Communication",
                "Speaking practice",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 5eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "4E"): {
        "display_name": "Anglais 4eme — Soutien Scolaire",
        "short_description": "Present perfect, conditionals, passive voice et debat.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Present perfect (for / since)",
                "Past continuous",
                "Passive voice",
                "The American Dream",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Conditionals (0, 1, 2)",
                "Reported speech (introduction)",
                "Science and Innovation",
                "Debate skills",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Relative clauses",
                "Used to",
                "Expressing opinions",
                "Multicultural societies",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc 4eme",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "3E"): {
        "display_name": "Anglais 3eme — Soutien Scolaire (Brevet)",
        "short_description": "Revision des temps, reported speech, argumentation et preparation Brevet.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Tenses review (all tenses)",
                "Reported speech",
                "Citizenship and Engagement",
                "Reading and Analysis",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Conditional 3",
                "Passive voice (advanced)",
                "Art and Power",
                "Argumentative writing",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Idioms and Phrasal verbs",
                "Cultural landmarks (UK / US / World)",
                "Revisions Brevet",
                "Oral practice",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Brevet blanc complet (anglais)",
                "Correction et analyse",
                "Methodologie de l'epreuve",
            ]},
        ],
    },
    ("ANG", "2NDE"): {
        "display_name": "Anglais Seconde — Soutien Scolaire",
        "short_description": "Consolidation grammaticale, themes culturels et comprehension avancee.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Vivre entre generations",
                "Tenses consolidation",
                "Grammar advanced (modals, gerund, infinitive)",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Les univers professionnels",
                "Le village, le quartier, la ville",
                "Comprehension orale et ecrite",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Representation de soi et rapport a autrui",
                "Sauver la planete",
                "Expression ecrite et orale",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc Seconde",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "1ERE"): {
        "display_name": "Anglais Premiere — Soutien Scolaire",
        "short_description": "Axes culturels, essay writing et preparation aux epreuves E3C.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Identites et echanges",
                "Espace prive, espace public",
                "Essay writing",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Art et pouvoir",
                "Citoyennete et mondes virtuels",
                "Comprehension avancee",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Fictions et realites",
                "Innovations scientifiques",
                "Preparation E3C / Bac",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Revision complete",
                "Examen blanc Premiere",
                "Correction et analyse",
            ]},
        ],
    },
    ("ANG", "TERM"): {
        "display_name": "Anglais Terminale — Soutien Scolaire (Bac)",
        "short_description": "Axes culturels avances, argumentation et preparation au Bac et Grand oral.",
        "structure": [
            {"chapter": "Trimestre 1", "sequentials": [
                "Identites et echanges",
                "Espace prive, espace public",
                "Essay and Synthesis",
            ]},
            {"chapter": "Trimestre 2", "sequentials": [
                "Art et pouvoir",
                "Citoyennete et mondes virtuels",
                "Debate and Argumentation",
            ]},
            {"chapter": "Trimestre 3", "sequentials": [
                "Diversite et inclusion",
                "Territoire et memoire",
                "Revisions Bac et Grand oral",
            ]},
            {"chapter": "Evaluation finale", "sequentials": [
                "Bac blanc complet (anglais)",
                "Simulation Grand oral",
                "Correction et analyse",
            ]},
        ],
    },
}

# Mapping level code -> display label for course key generation
LEVELS = [
    ("CM2", "CM2"),
    ("6E", "6eme"),
    ("5E", "5eme"),
    ("4E", "4eme"),
    ("3E", "3eme"),
    ("2NDE", "Seconde"),
    ("1ERE", "Premiere"),
    ("TERM", "Terminale"),
]

SUBJECTS = ["MATH", "FR", "ANG"]


def _build_course_list():
    """Return a list of dicts describing the 24 courses to create."""
    courses = []
    order = 0
    for level_code, _level_label in LEVELS:
        for subj in SUBJECTS:
            key = (subj, level_code)
            cur = CURRICULUM[key]
            code = f"{subj}-{level_code}"
            course_key_str = f"course-v1:{ORG}+{code}+{SESSION}"
            order += 1
            courses.append({
                "code": code,
                "course_key_str": course_key_str,
                "display_name": cur["display_name"],
                "short_description": cur["short_description"],
                "structure": cur["structure"],
                "order": order,
            })
    return courses


class Command(BaseCommand):
    help = "Create the AJEP academy and 24 courses (8 levels x 3 subjects) with full curriculum structure."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            default=False,
            help="Print what would be done without making any changes.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("=== DRY RUN — aucune modification ===\n"))

        # ------------------------------------------------------------------
        # 1. Academy
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("1/3  Creation de l'academie AJEP"))

        academy = Academy.objects.filter(slug="ajep").first()
        if academy:
            self.stdout.write(f"  -> Academie AJEP existe deja (id={academy.pk}), skip.")
        elif dry_run:
            self.stdout.write("  -> [DRY-RUN] Creerait l'academie AJEP.")
            academy = None
        else:
            academy = Academy.objects.create(
                name="Academie AJEP",
                short_name="AJEP",
                slug="ajep",
                academy_type=Academy.ACADEMY_TYPE_B2B,
                client_name="Association AJEP",
                description=(
                    "Avenir - Jeunesse - Entraide - Partage. "
                    "Soutien scolaire pour les jeunes de Pierrefitte-sur-Seine."
                ),
                primary_color="#0965D0",
                secondary_color="#01E8AE",
                max_seats=0,
                organization_id="AJEP",
                is_active=True,
            )
            self.stdout.write(self.style.SUCCESS(f"  -> Academie AJEP creee (id={academy.pk})."))

        # ------------------------------------------------------------------
        # 2. Courses in modulestore
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n2/3  Creation des 24 cours dans le modulestore"))

        store = modulestore()
        courses_def = _build_course_list()
        created_count = 0
        skipped_count = 0

        for idx, cdef in enumerate(courses_def, 1):
            course_key = CourseKey.from_string(cdef["course_key_str"])
            tag = f"  [{idx:02d}/24] {cdef['course_key_str']}"

            # Check if course already exists
            existing = store.get_course(course_key)
            if existing is not None:
                self.stdout.write(f"{tag}  EXISTE — skip")
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(f"{tag}  [DRY-RUN] {cdef['display_name']}")
                for section in cdef["structure"]:
                    self.stdout.write(f"           {section['chapter']}: {', '.join(section['sequentials'])}")
                continue

            # Create the course
            try:
                with store.default_store(ModuleStoreEnum.Type.split):
                    course = store.create_course(
                        org=course_key.org,
                        course=course_key.course,
                        run=course_key.run,
                        user_id=ModuleStoreEnum.UserID.mgmt_command,
                        fields={
                            "display_name": cdef["display_name"],
                            "short_description": cdef["short_description"],
                        },
                    )
            except DuplicateCourseError:
                self.stdout.write(f"{tag}  DUPLICATE — skip")
                skipped_count += 1
                continue

            # Create course structure (chapters + sequentials)
            for section in cdef["structure"]:
                chapter = store.create_child(
                    user_id=ModuleStoreEnum.UserID.mgmt_command,
                    parent_usage_key=course.location,
                    block_type="chapter",
                    fields={"display_name": section["chapter"]},
                )
                for seq_name in section["sequentials"]:
                    store.create_child(
                        user_id=ModuleStoreEnum.UserID.mgmt_command,
                        parent_usage_key=chapter.location,
                        block_type="sequential",
                        fields={"display_name": seq_name},
                    )

            created_count += 1
            self.stdout.write(self.style.SUCCESS(f"{tag}  CREE — {cdef['display_name']}"))

        self.stdout.write(f"\n  Resultat: {created_count} crees, {skipped_count} existants.")

        # ------------------------------------------------------------------
        # 3. AcademyCourse links
        # ------------------------------------------------------------------
        self.stdout.write(self.style.MIGRATE_HEADING("\n3/3  Liaison AcademyCourse"))

        if academy is None and not dry_run:
            academy = Academy.objects.filter(slug="ajep").first()

        linked_count = 0
        for idx, cdef in enumerate(courses_def, 1):
            if dry_run:
                self.stdout.write(f"  [DRY-RUN] Lierait {cdef['course_key_str']} -> AJEP")
                continue

            if academy is None:
                self.stdout.write(self.style.ERROR("  Academie introuvable, impossible de lier les cours."))
                break

            _, created = AcademyCourse.objects.get_or_create(
                academy=academy,
                course_key=cdef["course_key_str"],
                defaults={
                    "is_featured": False,
                    "order": cdef["order"],
                },
            )
            if created:
                linked_count += 1
                self.stdout.write(f"  [{idx:02d}] {cdef['course_key_str']}  -> lie")
            else:
                self.stdout.write(f"  [{idx:02d}] {cdef['course_key_str']}  -> deja lie")

        if not dry_run:
            self.stdout.write(f"\n  {linked_count} nouveaux liens crees.")

        # ------------------------------------------------------------------
        # Done
        # ------------------------------------------------------------------
        self.stdout.write(self.style.SUCCESS("\nTermine. 24 cours AJEP avec programmes complets."))
