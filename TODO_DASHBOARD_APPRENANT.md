# TODO Dashboard Apprenant

Date de mise a jour: 2026-02-21

## A faire

- [ ] Connecter `Forum`/`Tchat` (actuellement `href="#"`) dans `/Users/zakiachabane/edx-platform/themes/mission-theme/lms/templates/_mf_dashboard_sidebar.html`.
- [ ] Connecter les evenements `Planning` et les boutons `Google/Outlook/iCal` a une source de donnees reelle (actuellement statique dans `/Users/zakiachabane/edx-platform/themes/mission-theme/lms/templates/dashboard.html`).
- [ ] Connecter `Recommande`, `Notifications` et `Badges` a des donnees reelles (actuellement statique).
- [ ] Gerer les URLs certificats quand `download_url` est vide pour garantir PDF/preview.
- [X] Remplacer les valeurs hardcodees d'academies/progression (`VTC 73%`, `IT 42%`) par des donnees backend.
- [ ] Detecter le vrai mode de cours (`presentiel/distanciel`) au lieu de `data-mode="distanciel"` force.
- [ ] Finaliser les libelles/microcopie (terminologie FR uniforme: Email/Courriel, accents, ponctuation).
- [ ] Ajouter des tests de non-regression JS dashboard (filtres, certificats, progression, liens).
- [ ] Valider le responsive mobile + accessibilite clavier/ARIA.

## TODO demain (2026-02-22)

- [ ] Verifier l'acces `stagiaire`:
  - doit voir uniquement `/dashboard` apprenant.
  - ne doit pas acceder a `/admin/mission-dashboard/` (attendu: 403 ou redirection login).
- [ ] Verifier l'acces `formateur`:
  - doit voir uniquement son dashboard formateur sur `/dashboard`.
  - ne doit pas acceder a `/admin/mission-dashboard/` (attendu: 403).
- [ ] Verifier l'acces `superadmin`:
  - doit etre redirige de `/dashboard` vers `/admin/mission-dashboard/`.
  - doit charger le dashboard admin complet (sidebar + body + onglets actifs).
- [ ] Tester le cycle complet deconnexion/reconnexion pour les 3 profils ci-dessus en navigation privee.
- [ ] Ajouter une checklist de validation manuelle par rôle dans la documentation de deploiement (`custom-infra/docs/mission-openedx-lms-cms.md`).

## Notes

- Le dashboard formateur n'est pas demarre dans cette TODO (scope apprenant uniquement).
