# Relecture 11 : cadrage-orca-reference, intégration de `main`

Relecteur seul, les deux axes (relecture d'un cadrage). Périmètre : `git diff HEAD` (résolution des conflits et alignements) et `git diff origin/main` sur `docs/decisions/0009-permissions-par-role.md`, `docs/decisions/README.md`, `docs/process/roles/`, `docs/specs/OPEN-QUESTIONS.md`, `docs/specs/RETOURS.md` et `docs/references/orca.md`. Lus en plus pour la cohérence : ADR 0013, 0014 et 0015, `docs/process/README.md` (remontée, signalement, lancement), `AGENTS.md`, `GLOSSARY.md`.

## Vérifications

- **Marqueurs de conflit** : aucun dans le repo, hors `docs/plans/` (non parcouru, comme demandé).
- **Apports de `main`** : rien de perdu ni d'altéré. Face à `origin/main`, la branche n'ajoute que du texte. Les lignes remplacées gardent celui de `main` mot pour mot et le complètent : statut de l'ADR 0009, paragraphe `Edit(./**)` de l'implémenteur, permissions d'écriture de l'orchestrateur de tâche, étape « Étapes » du planificateur (passée de 3 à 4 avec sa phrase sur la liste blanche), Q-036.
- **Numérotation** :
  - RET-011 entre RET-010 et RET-012 ;
  - Q-035 à Q-043 dans l'ordre, puis Q-050 et Q-051, sans doublon ;
  - ADR 0014 entre 0013 et 0015 dans l'index ;
  - sections du plan du planificateur renumérotées de 1 à 8 sans trou.
- **Statuts** :
  - ADR 0014 acceptée (fichier et index) ;
  - RET-011 appliqué ;
  - le statut de l'ADR 0009 garde les compléments de main (ADR 0012, 0013) et ajoute la précision de l'ADR 0014, comme le demande l'ADR 0014 ;
  - Q-042 tranchée, avec sa raison ;
  - le porteur de Q-043 passe à l'orchestrateur de tâche, conforme à l'ADR 0013, puisqu'il lance le planificateur.
- **Cohérence avec les ADR 0013 et 0015** :
  - aucun message au coordinateur. Une erreur de la carte remonte avec le feu vert plan, dans le commentaire de la carte Orca (`orca.md`, §0) ;
  - l'accord pour `chmod` ou la suppression du clone passe par `⛔ bloqué : …`, posé avant l'invite. C'est conforme à la table « Signalement d'attente » et à la conséquence de l'ADR 0015 : bloqué sur une invite, l'orchestrateur de tâche ne peut plus mettre à jour sa carte ;
  - l'écriture dans le dossier du clone, ajoutée au profil de l'orchestrateur de tâche, reste dans le tableau de l'ADR 0013 (« dossiers temporaires »), puisque le clone est dans un dossier temporaire du poste. Q-036 en tient compte pour la garde ;
  - glossaire (« Clone de référence ») et `AGENTS.md`, règle 9 : alignés.
- **Chemins machine** : aucun dans `docs/`, `AGENTS.md` ni `README.md`. Le clone est toujours désigné par `<clone-orca>`, et les fichiers d'Orca par leur chemin dans le repo d'Orca.

## Constats

### Bloquant

Aucun.

### À corriger

Aucun.

### Suggestions

1. `docs/specs/RETOURS.md:164` : le statut indique « intégration de `main` relue au tour 10 ». La relecture de l'intégration continue au tour 11 : la mention sera incomplète au commit. Correction proposée : « intégration de `main` relue » sans numéro de tour, ou le numéro du tour qui conclut OK.
2. `docs/process/roles/orchestrateur-tache.md:31` : « Il prépare ou refait donc le clone avant de lancer le planificateur ». La vérification a lieu avant **chaque** lancement qui reçoit le clone, donc aussi avant l'implémenteur en cas de reprise, et elle peut alors exiger de refaire le clone, avec la même invite. Correction proposée : « avant de lancer le rôle qui le reçoit ».
3. Hors contenu, pour l'orchestrateur de tâche, avant le commit de fusion :
   - l'index marque encore `UU` les six fichiers résolus ;
   - `docs/references/orca.md` et `docs/process/roles/orchestrateur-tache.md` portent des modifications non indexées (` M`, `AM`).

   Il faut les ajouter à l'index pour que le commit de fusion contienne la résolution relue ici.

RELECTURE : OK
