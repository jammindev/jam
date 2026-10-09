# Relecture du cadrage `cadrage-orca-reference`, tour 2

Relecteur seul, deux axes. Objet : la rédaction non commitée qui applique RET-011 (`git diff`, 8 fichiers : `AGENTS.md`, profils de l'implémenteur, du planificateur et du relecteur, `docs/references/orca.md`, glossaire, `OPEN-QUESTIONS.md`, `RETOURS.md`).

> Écart au profil, signalé par transparence : le rapport du tour 1 (`cadrage-orca-reference-relecture-1.md`) a été ouvert par erreur en début de relecture, avant la lecture du diff. Les constats ci-dessous viennent de la relecture du diff et des docs. Aucun ne reprend un constat du tour 1.

Vérifié sans constat :
- les cinq points de la règle validée figurent dans RET-011, dans le profil du planificateur et dans `AGENTS.md` (règle 9) ;
- la portée « tâches de jam seulement » est cohérente entre le profil du planificateur (lignes 13, 15, 20), la carte (ligne 18), RET-011 (ligne 99) et Q-040. Elle tient avec le jalon S2, qui fait tourner le planificateur sur `house` ;
- l'ADR 0001 n'est pas contournée : pas de fork, mention de licence dans le fichier repris et dans `THIRD_PARTY_NOTICES.md`, comme elle le prévoit. Pas de nouvelle ADR, c'est justifié ;
- la liste noire est conforme aux ADR 0002 (ligne 25) et 0004 (option 1). Le §9 de la carte marque désormais les terminaux comme écartés ;
- la citation « on n'élague pas le code d'Orca » est exacte (`00-VISION.md`, ligne 49) ; l'ADR 0005 cite bien la reprise des briques d'Orca parmi ses critères ;
- la renumérotation de la structure du plan (3 à 8) ne casse aucun renvoi dans les docs ;
- `THIRD_PARTY_NOTICES.md` n'existe pas encore : « rien n'a été repris jusqu'ici » est exact ;
- aucun chemin propre à une machine : le clone est désigné par `<clone-orca>`, et le plan cite les fichiers d'Orca par leur chemin dans le repo d'Orca ;
- les renvois de section de la carte (§1 à §9) et le risque R-03 existent ;
- le complément sur l'implémenteur est bien présenté comme une proposition à valider (RET-011, implémenteur, glossaire) ;
- la numérotation (RET-011, Q-040, Q-042) respecte le partage avec l'autre cadrage.

## Bloquant

Aucun.

## À corriger

### 1. La carte désigne des dossiers entiers, pas « quelques fichiers »

- **Fichier** : `docs/references/orca.md`, lignes 33 et 39 (et dans une moindre mesure ligne 36).
- **Constat** : selon la règle validée (point 1) et le profil du planificateur (ligne 15), le planificateur lit « dans le clone, les quelques fichiers qu'elle désigne ». Or la première ligne du tableau renvoie à `src/main/` (environ 230 sous-dossiers, §1, ligne 63), `src/preload/` et `src/shared/rpc-contract/`, et la dernière renvoie à `src/main/runtime/orchestration/`, un sous-dossier de `runtime/`, qui compte environ 1 500 fichiers. Ces lignes invitent à l'exploration que la règle interdit, et le coût en quota que RET-011 veut éviter (ligne 90) revient par la carte.
- **Correction attendue** : pour chaque ligne qui pointe vers un dossier, nommer le ou les fichiers d'entrée à lire, relevés au tag (par exemple le point d'entrée du processus main, le contrat RPC, `preamble.ts` et le schéma de la base d'orchestration, déjà cités en §2 et §6). À défaut, écrire dans la cellule « point d'entrée seulement, à relever au tag », pour que la limite soit lisible dans la carte elle-même.

### 2. Un clone réutilisé dans un dossier temporaire peut être purgé en partie sans que personne le voie

- **Fichier** : `docs/references/orca.md`, lignes 22 et 29 ; `docs/specs/OPEN-QUESTIONS.md`, ligne 41 (Q-042).
- **Constat** : la carte place le clone dans « un dossier temporaire du poste » et le réutilise pour toutes les tâches tant que la version ne change pas. Or sur macOS, `/tmp` est vidé au redémarrage, et les dossiers temporaires peuvent être purgés des fichiers non lus depuis quelques jours. Le retrait des droits d'écriture n'empêche pas cette purge, qui tourne avec les droits du système. Un clone purgé en partie ne se voit pas : le planificateur appliquerait alors la règle de la ligne 20 (« un fichier introuvable au tag se cherche par son nom, et l'écart est signalé dans le plan ») et attribuerait à un changement de version un fichier simplement effacé.
- **Correction attendue** : ajouter à la procédure une vérification avant chaque lancement d'un rôle qui reçoit le clone, faite par l'orchestrateur de tâche. Le clone doit exister, `git -C <clone-orca> status --porcelain` doit être vide, et `git -C <clone-orca> describe --tags --exact-match` doit renvoyer `v1.4.218`. Sinon, l'orchestrateur supprime le clone et le refait. Reprendre cette vérification dans Q-042, avec la préparation du clone.

### 3. La justification du complément sur l'implémenteur repose sur une affirmation non vérifiée

- **Fichiers** : `docs/specs/RETOURS.md`, ligne 98 ; `docs/process/roles/implementeur.md`, ligne 18 ; `docs/specs/GLOSSARY.md`, ligne 35.
- **Constat** : RET-011 affirme que, sans `--add-dir`, « l'implémenteur ne peut copier ni le morceau repris ni le texte de la licence ». Or la commande de l'implémenteur, comme celles du planificateur et du relecteur, autorise `"Read"` sans restriction de chemin. Dans Claude Code, une telle règle couvre la lecture de n'importe quel fichier, y compris hors du worktree : l'implémenteur pourrait donc probablement lire le clone dès qu'il en connaît le chemin. Ce qui ouvre réellement le clone serait alors le chemin donné dans le brief. `--add-dir` ajouterait surtout le dossier à l'espace de travail, par exemple pour `Glob` et `Grep`. Le mainteneur trancherait ce complément au feu vert de cadrage sur une base peut-être inexacte, et le glossaire (« L'orchestrateur de tâche l'ouvre au planificateur… ») laisse croire à un contrôle d'accès qui n'existe pas.
- **Correction attendue** :
  - dans RET-011, remplacer la phrase par ce que fait le complément : « pour une reprise, le brief de l'implémenteur lui donne le chemin du clone, et l'orchestrateur l'ajoute par `--add-dir` ». Retirer « ne peut » ou le marquer comme à vérifier ;
  - dans le glossaire, préciser que l'accès tient au chemin donné dans le brief et à `--add-dir`, sans contrôle des lectures ;
  - tracer la vérification (une règle `"Read"` sans restriction lit-elle hors du worktree en `dontAsk` ? qu'apporte alors `--add-dir` ?) dans une question ouverte, sur le modèle de Q-033 (Q-043, ou un ajout à Q-042).

## Suggestions

### 4. Ce que `--add-dir` charge depuis le clone

- **Fichier** : `docs/references/orca.md`, lignes 23 à 26.
- **Constat** : Claude Code peut charger certains réglages d'un dossier ajouté par `--add-dir`, notamment les skills de son dossier `.claude/skills/`, si le dossier en contient. Le clone d'un repo tiers pourrait ainsi injecter des consignes dans le contexte du planificateur. Le comportement exact est à vérifier : `CLAUDE.md` n'est pas chargé par défaut, mais les skills le seraient.
- **Proposition** : vérifier si le clone au tag contient un dossier `.claude/`. Si c'est le cas, ajouter `rm -rf <clone-orca>/.claude` à la procédure, avant le `chmod`, et le dire en une ligne.

### 5. La limite du relecteur sur les copies déguisées peut être levée à moindre coût

- **Fichier** : `docs/process/roles/relecteur.md`, ligne 28.
- **Constat** : le point 5 note que, sans accès au clone, le relecteur ne repère pas une copie présentée comme « inspirée ». Le relecteur a lui aussi `"Read"` sans restriction (voir le constat 3). Lui donner le chemin du clone suffirait sans doute. Telle quelle, la limite n'est pas tracée dans `OPEN-QUESTIONS.md`, contrairement à ce que demande `AGENTS.md` (règle 4) pour ce qui est remis à plus tard.
- **Proposition** : quand la section « Orca » du plan cite un fichier « repris » ou « inspiré », le brief du relecteur de conformité donne le chemin du clone. À défaut, noter la limite dans Q-042.

### 6. Le process ne dit pas encore que le brief porte le chemin du clone

- **Fichier** : `docs/process/README.md`, ligne 36 (table de correspondance, ligne « Plan ») et ligne 62 (contenu du brief).
- **Constat** : le profil du planificateur dit que « le brief en donne le chemin », mais la liste de ce que contient « toujours » le brief (ligne 62) et la table de correspondance n'en parlent pas.
- **Proposition** : ajouter à la ligne 62 « pour une tâche de jam qui touche une brique d'Orca, le chemin du clone de référence (RET-011) ». Ce point peut aussi être reporté à la fusion avec le cadrage de l'orchestrateur, en l'ajoutant à Q-042.

RELECTURE : CORRECTIONS (3)
