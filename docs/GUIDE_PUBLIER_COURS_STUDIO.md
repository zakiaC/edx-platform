# Guide — Publier un cours et le rattacher a une academie

## Mission Formations — OpenEdX Studio

> Version 1.0 — 24 mars 2026
> Pour : Admins, Formateurs

---

## 1. Creer un cours dans Studio

### Acces Studio
- URL : **https://apps.academie.staging.missionformations.com/authoring/home**
- Se connecter avec un compte staff ou admin

### Creer un nouveau cours
1. Cliquer **"Nouveau cours"** sur la page d'accueil Studio
2. Remplir les champs :
   - **Nom du cours** : ex. "Strategie Commerciale"
   - **Organisation** : MissionFormations
   - **Numero** : ex. MF-STRAT-COM-2026
   - **Session** : ex. 2026
3. Cliquer **"Creer"**

---

## 2. Importer un cours OLX

Si le cours a ete prepare en format OLX (tar.gz) :

1. Ouvrir le cours dans Studio
2. Aller dans **Outils** → **Importer**
3. Cliquer **"Choisir un fichier"** et selectionner le fichier `.tar.gz`
4. Cliquer **"Remplacer le contenu du cours"**
5. Attendre la fin de l'import (peut prendre quelques minutes)

---

## 3. Structurer le contenu manuellement

### Hierarchie OpenEdX
```
Cours
└── Section (= Module/Chapitre)
    └── Sous-section (= Lecon)
        └── Unite (= Page avec composants)
            ├── Video
            ├── Texte HTML
            └── Quiz
```

### Ajouter une section
1. Dans le cours, cliquer **"+ Nouvelle section"**
2. Nommer la section (ex. "Module 1 — Qui est votre client ?")

### Ajouter une sous-section
1. Dans la section, cliquer **"+ Nouvelle sous-section"**
2. Nommer la sous-section (ex. "Les cas particuliers")

### Ajouter une unite
1. Dans la sous-section, cliquer **"+ Nouvelle unite"**
2. Ajouter des composants :
   - **Video** : coller le lien YouTube ou uploader un fichier
   - **Texte** : editeur HTML pour le contenu textuel
   - **Probleme** : quiz (QCM, reponse libre, etc.)

---

## 4. Ajouter une video YouTube

1. Dans une unite, cliquer **"+ Ajouter un composant"** → **"Video"**
2. Cliquer sur **"Modifier"** (icone crayon)
3. Dans le champ **"URL de la video"**, coller le lien YouTube
   - Format : `https://youtu.be/XXXXX` ou `https://www.youtube.com/watch?v=XXXXX`
4. Remplir le **titre** de la video
5. Cliquer **"Enregistrer"**

---

## 5. Ajouter un cours manuellement (sans import OLX)

Si vous creez un cours de zero ou ajoutez du contenu a un cours existant :

### Etape 1 : Creer la structure

1. Ouvrir le cours dans Studio
2. Cliquer **"+ Nouvelle section"** pour chaque module/chapitre
3. Dans chaque section, cliquer **"+ Nouvelle sous-section"** pour chaque lecon
4. Dans chaque sous-section, cliquer **"+ Nouvelle unite"** pour chaque page

### Etape 2 : Ajouter le contenu a une unite

Chaque unite peut contenir plusieurs composants :

**Ajouter un texte d'introduction :**
1. Dans l'unite, cliquer **"+ Ajouter un composant"** → **"Texte"**
2. Ecrire ou coller le contenu dans l'editeur HTML
3. Cliquer **"Enregistrer"**

**Ajouter une video YouTube :**
1. Cliquer **"+ Ajouter un composant"** → **"Video"**
2. Cliquer sur **"Modifier"** (icone crayon)
3. Coller le lien YouTube dans le champ URL
4. Remplir le titre
5. Cliquer **"Enregistrer"**

**Ajouter un quiz :**
1. Cliquer **"+ Ajouter un composant"** → **"Probleme"**
2. Choisir le type : QCM, reponse libre, vrai/faux, etc.
3. Remplir la question, les reponses et la bonne reponse
4. Cliquer **"Enregistrer"**

### Etape 3 : Reorganiser le contenu

- **Glisser-deposer** les sections, sous-sections et unites pour changer l'ordre
- Cliquer sur les **3 barres** (icone hamburger) a gauche d'un element et le faire glisser
- La reorganisation est sauvegardee automatiquement

### Etape 4 : Publier

- Apres chaque ajout ou modification, cliquer **"Publier"** sur la section concernee
- Un indicateur jaune signale du contenu non publie

### Exemple concret : ajouter une video manquante

Scenario : le Module 2 du cours "Strategie Commerciale" n'a pas la video 2.1.

1. Ouvrir le cours dans Studio
2. Cliquer sur **Module 2 — Connaitre le parcours d'achat**
3. En haut de la sous-section, cliquer **"+ Nouvelle unite"**
4. Nommer l'unite : "Prerequis — Le parcours d'achat en 4 etapes"
5. Ajouter un composant **Texte** avec l'introduction :
   > Avant de plonger dans le parcours d'achat, decouvrez les 4 etapes fondamentales
   > que traverse chaque client : prise de conscience, consideration, decision et fidelisation.
6. Ajouter un composant **Video** avec le lien YouTube : `https://youtu.be/G08amhiHG-s`
7. **Publier** l'unite
8. **Glisser-deposer** l'unite en premiere position du module 2

---

## 6. Publier le cours

### Publier section par section
1. Ouvrir le cours dans Studio
2. Cliquer sur une **section** (ex. Module 0)
3. En haut a droite, cliquer le bouton **"Publier"**
4. Confirmer
5. Repeter pour chaque section

### Verifier la publication
- Une section publiee a un indicateur vert
- Une section en brouillon a un indicateur jaune
- Les modifications non publiees apparaissent avec un avertissement

### Rendre le cours accessible
1. Aller dans **Parametres** → **Planning et details** (Schedule & Details)
2. Verifier la **date de debut** (doit etre passee ou aujourd'hui)
3. Verifier la **date d'inscription** (doit etre ouverte)
4. **Enregistrer**

---

## 7. Rattacher un cours a une academie

### Via le dashboard admin LMS

1. Se connecter sur le LMS : **https://academie.staging.missionformations.com/admin/mission-dashboard/**
2. Aller dans **Academy Manager**
3. Selectionner l'academie (ex. "Finance")
4. Cliquer **"Ajouter un cours"**
5. Selectionner le cours (ex. "course-v1:MissionFormations+MF-STRAT-COM-2026+2026")
6. Enregistrer

### Via Django Admin

1. Aller sur **https://academie.staging.missionformations.com/admin/**
2. Chercher **AcademyCourse** dans les modeles mission_central_admin
3. Cliquer **"Ajouter"**
4. Remplir :
   - **Academy** : selectionner l'academie
   - **Course ID** : `course-v1:MissionFormations+MF-STRAT-COM-2026+2026`
   - **Featured** : cocher si le cours doit apparaitre en avant
   - **Order** : position d'affichage (1 = premier)
5. Enregistrer

### Via le shell Django (avance)

```bash
ssh staging-openedx
docker exec -it tutor_local_lms_1 bash
python manage.py lms shell
```

```python
from lms.djangoapps.mission_central_admin.models import Academy, AcademyCourse
from opaque_keys.edx.keys import CourseKey

academy = Academy.objects.get(slug='finance')
course_key = CourseKey.from_string('course-v1:MissionFormations+MF-STRAT-COM-2026+2026')
AcademyCourse.objects.create(academy=academy, course_id=course_key, featured=True, order=1)
```

---

## 8. Inscrire des apprenants

### Inscription manuelle (Studio)

1. Dans le cours, aller dans **Membres de l'equipe** → **Inscription**
2. Entrer les emails des apprenants (un par ligne)
3. Cliquer **"Inscrire"**

### Inscription via l'admin Django

1. Aller sur `/admin/` → **CourseEnrollment**
2. Ajouter une inscription : utilisateur + cours + mode (audit/honor)

### Auto-inscription via le catalogue

Si le cours est rattache a une academie et visible dans le catalogue :
- Les apprenants peuvent s'inscrire eux-memes depuis `/catalogue/`
- Cliquer sur le cours → **"S'inscrire"**

---

## 9. Guide par role

### Pour le formateur
1. Se connecter a Studio
2. Creer/modifier le contenu du cours
3. Publier les sections modifiees
4. Suivre les notes dans l'onglet **"Notes"** du cours LMS
5. Exporter les resultats en CSV depuis le dashboard admin

### Pour l'admin
1. Creer les cours dans Studio
2. Rattacher aux academies
3. Gerer les inscriptions
4. Suivre les KPIs dans le dashboard admin
5. Generer les documents Qualiopi (attestations, emargement)

### Pour l'apprenant
1. Se connecter sur le LMS : **https://academie.staging.missionformations.com/**
2. Aller dans **Catalogue** ou **Dashboard**
3. S'inscrire a un cours
4. Suivre les videos module par module
5. Passer les quiz
6. Consulter sa progression
7. Telecharger son certificat une fois termine

---

## 10. Checklist publication d'un cours

- [ ] Cours cree dans Studio (org, numero, session)
- [ ] Contenu importe ou cree manuellement
- [ ] Toutes les videos fonctionnent (tester chaque lien YouTube)
- [ ] Quiz ajoutes a chaque fin de module
- [ ] Date de debut correcte (Schedule & Details)
- [ ] Inscription ouverte
- [ ] Toutes les sections publiees (indicateur vert)
- [ ] Cours rattache a l'academie (AcademyCourse)
- [ ] Cours visible dans le catalogue
- [ ] Test parcours apprenant complet (inscription → video → quiz → certificat)
- [ ] Description du cours remplie (About page)
- [ ] Image du cours uploadee

---

*Document genere le 24 mars 2026 — Mission Formations*
